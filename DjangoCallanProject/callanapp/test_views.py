from django.test import TestCase
from django.urls import reverse

class ViewsTest(TestCase):

    def test_login_redirect(self):
        response = self.client.get(
        reverse('usersapp:login'))  # Используйте reverse с именем вашего URL-паттерна для страницы входа
        self.assertEqual(response.status_code, 200)  # Или 302, в зависимости от ожидаемого кода ответа


    def test_index_redirect(self):
        # Создаем запрос к защищенному представлению
        response = self.client.get(reverse('index'))

        # Проверяем, что код ответа равен 302 (перенаправление)
        self.assertEqual(response.status_code, 302)

        # Проверяем, что пользователь перенаправляется на страницу входа
        self.assertRedirects(response, f"{reverse('usersapp:login')}?next={reverse('index')}")

        # Проверяем, что в URL страницы входа присутствует параметр 'next'
        self.assertIn('next', response.url)



    def test_dictation_stage_redirect(self):
        response = self.client.get(reverse('dictation_stage'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('usersapp:login')}?next={reverse('dictation_stage')}")  # Исправлено на 'dictation_stage'
        self.assertIn('next', response.url)



    def test_read_student_book_redirect(self):
        response = self.client.get(reverse('read_student_book'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('usersapp:login')}?next={reverse('read_student_book')}")
        self.assertIn('next', response.url)

    def test_select_stage_word_redirect(self):
        response = self.client.get(reverse('select_stage_word'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('usersapp:login')}?next={reverse('select_stage_word')}")
        self.assertIn('next', response.url)