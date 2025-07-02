import pytest
from django.urls import reverse
from http import HTTPStatus
from django.conf import settings

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 5):
        News.objects.create(title=f'Новость {i}', text='Текст новости', date='2025-01-01')

    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']
    assert len(news_list) <= settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_ordering_on_home_page(client):
    News.objects.create(title='Старая новость', text='...', date='2020-01-01')
    News.objects.create(title='Свежая новость', text='...', date='2025-01-01')

    response = client.get(reverse('news:home'))
    news_list = response.context['object_list']
    dates = [news.date for news in news_list]
    assert dates == sorted(dates, reverse=True)  


@pytest.mark.django_db
def test_comments_ordering_on_news_detail(client, django_user_model):
    news = News.objects.create(title='Новость', text='...', date='2025-01-01')
    user = django_user_model.objects.create_user(username='user')

    Comment.objects.create(news=news, author=user, text='Первый комментарий')
    Comment.objects.create(news=news, author=user, text='Второй комментарий')

    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    comments = response.context['news'].comment_set.all()
    created_times = [c.created for c in comments]
    assert created_times == sorted(created_times)  


@pytest.mark.django_db
def test_comment_form_visibility(client, django_user_model):
    user = django_user_model.objects.create_user(username='user')
    news = News.objects.create(title='Новость', text='...', date='2025-01-01')

    url = reverse('news:detail', args=(news.pk,))

   
    response = client.get(url)
    assert 'form' not in response.context


    client.force_login(user)
    response = client.get(url)
    assert 'form' in response.context
    