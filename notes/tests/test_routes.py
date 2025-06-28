from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='Автор')
        cls.user_2 = User.objects.create(username='Пользователь_1')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.user_1
        )

    def test_pages_availability(self):
        """Публичные страницы доступны любому пользователю."""
        urls = (
            ('notes:home', 'get'),
            ('users:login', 'get'),
            ('users:logout', 'post'),
            ('users:signup', 'get'),
        )
        for name, method in urls:
            with self.subTest(name=name):
                url = reverse(name)
                client_method = getattr(self.client, method)
                response = client_method(url)
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
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_authorized_users(self):
        """Страницы list, add, detail доступны авторизованному пользователю."""
        self.client.force_login(self.user_1)
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_notes_edit_and_delete(self):
        """Проверка доступа к edit/delete для разных пользователей."""
        users_statuses = (
            (self.user_1, HTTPStatus.OK),
            (self.user_2, HTTPStatus.NOT_FOUND),
        )
        urls = (
            'notes:edit',
            'notes:delete',
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_success_page_available_for_authorized_user(self):
        """Страница выполнения доступна авторизованному пользователю."""
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('notes:success'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_to_success_after_note_creation(self):
        login_url = reverse('users:login')
        success_url = reverse('notes:success')
        redirect_url = f'{login_url}?next={success_url}'
        response = self.client.get(success_url)
        self.assertRedirects(response, redirect_url)
