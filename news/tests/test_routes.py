import pytest
from http import HTTPStatus
from pytest_lazy_fixtures import lf
from django.urls import reverse
from pytest_django.asserts import assertRedirects

@pytest.mark.parametrize(
    'name',
    ('news:home', 'news:detail'), 
)
def test_anonymous_pages_accessible(client, name, note):
    args = (note.pk,) if name == 'news:detail' else None
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'), 
)
def test_pages_availability_for_comment_author(author_client, name, comment):
    url = reverse(name, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK 


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('not_author_client'), HTTPStatus.NOT_FOUND),
        (lf('author_client'), HTTPStatus.OK)              
    ),
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'), 
)
def test_pages_availability_for_different_users(parametrized_client, name, comment, expected_status):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', lf('comment_pk')),
        ('news:delete', lf('comment_pk')),
    ),
)
def test_redirects_anonymous_to_login(client, name, args):
    login_url = reverse('users:login')
    url = reverse(name, args=(args,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:signup'),
)
def test_auth_pages_accessible_anonymous(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

def test_logout_redirect_anonymous(client):
    url = reverse('users:logout')
    response = client.get(url)
    assert response.status_code in (HTTPStatus.METHOD_NOT_ALLOWED, HTTPStatus.FOUND)
    