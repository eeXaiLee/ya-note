from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='Пользователь_1')
        cls.user_2 = User.objects.create(username='Пользователь_2')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user_1
        )

    def test_pages_availability(self):
        """Публичные страницы доступны любому пользователю."""
        urls = (
            ('notes:home', self.client.get),
            ('users:login', self.client.get),
            ('users:logout', self.client.post),
            ('users:signup', self.client.get),
        )
        for name, method in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = method(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_user(self):
        """Анонимный пользователь перенаправляется на страницу входа."""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_authorized_user_access(self):
        """Авторизованный пользователь имеет доступ к защищённым страницам."""
        self.client.force_login(self.user_1)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_delete_access_restriction(self):
        """Редактировать и удалять заметку может только автор."""
        users_statuses = (
            (self.user_1, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.logout()
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)
