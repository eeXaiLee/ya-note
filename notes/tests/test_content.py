from django.contrib.auth import get_user_model
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

    def test_note_detail_contains_content(self):
        """Страница заметки содержит заголовок и текст."""
        self.client.force_login(self.user_1)
        response = self.client.get(
            reverse('notes:detail', args=(self.note.slug,))
        )
        self.assertContains(response, self.note.title)
        self.assertContains(response, self.note.text)

    def test_form_fields_on_create_page(self):
        """Проверка отображения полей формы."""
        self.client.force_login(self.user_1)
        url = reverse('notes:add')
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NoteForm)
        fields = ['title', 'text', 'slug']
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(field, form.fields)
