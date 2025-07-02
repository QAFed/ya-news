import pytest
from django.urls import reverse
from http import HTTPStatus
from news.models import Comment
from news.forms import WARNING

@pytest.mark.django_db
def test_anonymous_cannot_post_comment(client, note):
    url = reverse('news:detail', args=(note.pk,))
    response = client.post(url, data={'text': 'Привет'})
    assert response.status_code == HTTPStatus.FOUND
    login_url = reverse('users:login')
    assert login_url in response.url

@pytest.mark.django_db
def test_authorized_can_post_comment(author_client, note):
    url = reverse('news:detail', args=(note.pk,))
    data = {'text': 'Новый комментарий'}
    response = author_client.post(url, data=data, follow=True)
    assert response.status_code == HTTPStatus.OK
    assert 'Новый комментарий' in response.content.decode()

@pytest.mark.django_db
def test_comment_with_bad_words_rejected(author_client, note):
    url = reverse('news:detail', args=(note.pk,))
    data = {'text': 'Ты редиска!'}  
    response = author_client.post(url, data=data)
    assert response.status_code == HTTPStatus.OK
    comments = Comment.objects.filter(news=note)
    assert comments.count() == 0
    assert WARNING in response.content.decode()

@pytest.mark.django_db
def test_author_can_edit_own_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    data = {'text': 'Отредактированный комментарий'}
    response = author_client.post(url, data=data, follow=True)
    assert response.status_code == HTTPStatus.OK
    assert 'Отредактированный комментарий' in response.content.decode()

@pytest.mark.django_db
def test_author_cannot_edit_others_comment(not_author_client, comment):
    url = reverse('news:edit', args=(comment.pk,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND

@pytest.mark.django_db
def test_author_can_delete_own_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = author_client.post(url, follow=True)
    assert response.status_code == HTTPStatus.OK
    response = author_client.get(reverse('news:detail', args=(comment.news.pk,)))
    assert comment.text not in response.content.decode()

@pytest.mark.django_db
def test_author_cannot_delete_others_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.pk,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND