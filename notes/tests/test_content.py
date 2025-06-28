from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user_1 = User.objects.create(username='Пользователь_1')
        cls.user_2 = User.objects.create(username='Пользователь_2')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Текст заметки',
            author=cls.user_1,
            slug='test-note'
        )
        cls.other_note = Note.objects.create(
            title='Автоматический slug',
            text='Текст заметки',
            author=cls.user_2
        )

    def test_user_sees_only_own_notes_in_list(self):
        """Проверка, что в списке только свои заметки."""
        self.client.force_login(self.user_1)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), 1)
        self.assertEqual(object_list[0].pk, self.note.pk)

    def test_note_detail_page_contains_correct_content(self):
        """Проверка содержимого страницы заметки."""
        self.client.force_login(self.user_1)
        response = self.client.get(
            reverse('notes:detail', args=(self.note.slug,))
        )
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_form_fields_visibility(self):
        """Проверка отображения полей формы."""
        form = NoteForm()
        fields = ['title', 'text', 'slug']
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, form.fields)

    def test_slug_auto_creation(self):
        """Проверка автоматического создания slug."""
        self.assertTrue(self.other_note.slug)
        self.assertEqual(self.other_note.slug, 'avtomaticheskij-slug')

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
