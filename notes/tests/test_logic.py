from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
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
        cls.note_auto_slug = Note.objects.create(
            title='Автоматический slug',
            text='Текст',
            author=cls.user_2
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

    def test_anonymous_user_cannot_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        url = reverse('notes:add')
        form_data = {
            'title': 'Анонимная заметка',
            'text': 'Текст',
            'slug': 'anon-note'
        }
        response = self.client.post(url, data=form_data)
        login_url = reverse('users:login')
        self.assertRedirects(response, f'{login_url}?next={url}')
        self.assertFalse(Note.objects.filter(slug='anon-note').exists())

    def test_slug_auto_creation(self):
        """Проверка автоматического создания slug."""
        self.assertEqual(self.note_auto_slug.slug, 'avtomaticheskij-slug')

    def test_unique_slug_validation(self):
        """Проверка валидации уникальности slug."""
        with self.assertRaises(ValidationError):
            note = Note(
                title='Новая заметка',
                text='Текст',
                author=self.user_1,
                slug='test-note'
            )
            note.full_clean()

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

    def test_other_user_cannot_edit_someone_elses_note(self):
        """Авторизованный пользователь не может редактировать чужую заметку."""
        self.client.force_login(self.user_2)
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.client.post(url, data={
            'title': 'Попытка',
            'text': 'Новый текст',
            'slug': 'test-note'
        })
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.text, 'Новый текст')

    def test_other_user_cannot_delete_someone_elses_note(self):
        """Авторизованный пользователь не может удалить чужую заметку."""
        self.client.force_login(self.user_2)
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.client.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(pk=self.note.pk).exists())
