# conftest.py
import pytest

# Импортируем класс клиента.
from django.test.client import Client

# Импортируем модель заметки, чтобы создать экземпляр.
from news.models import News
@pytest.fixture
def note(db):
    return News.objects.create(title='Заголовок', text='Текст')

@pytest.fixture
def author(db, django_user_model):
    user = django_user_model.objects.create_user(username='author', password='pass')
    return user

@pytest.fixture
def comment(db, note, author):
    from news.models import Comment
    return Comment.objects.create(news=note, author=author, text='Комментарий')

@pytest.fixture
def author_client(client, author):
    client.force_login(author)
    return client

@pytest.fixture
def not_author_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='not_author', password='pass')
    client.force_login(user)
    return client

@pytest.fixture
def comment_pk(comment):
    return comment.pk