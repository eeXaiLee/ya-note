from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestNoteLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        """Создание тестовых пользователей и заметки."""
        cls.user_1 = User.objects.create(username='Пользователь 1')
        cls.user_2 = User.objects.create(username='Пользователь 2')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.user_1,
            slug='test-note'
        )

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        self.client.force_login(self.user_1)
        url = reverse('notes:add')
        form_data = {
            'title': 'Новая заметка',
            'text': 'Текст заметки',
            'slug': 'new-note'
        }
        response = self.client.post(url, data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertTrue(Note.objects.filter(slug='new-note').exists())

    def test_author_can_edit_note(self):
        """Автор может получить страницу редактирования заметки."""
        self.client.force_login(self.user_1)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_can_delete_note(self):
        """Автор может удалить свою заметку."""
        self.client.force_login(self.user_1)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())
