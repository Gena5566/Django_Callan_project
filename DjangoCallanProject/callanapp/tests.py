from django.test import TestCase
from usersapp.models import BlogUser
from .models import  Word, SentEmail


# Create your tests here.

class WordModelTest(TestCase):
    def setUp(self):
        self.word = Word.objects.create(
            russian_word='Привет',
            english_translation='Hello',
            level='Stage 1'
        )

    def test_str_representation(self):
        expected_str = 'Привет (Stage 1)'
        self.assertIn(expected_str, str(self.word))


class SentEmailModelTest(TestCase):
    def setUp(self):
        self.user = BlogUser.objects.create(username='testuser', email='test@example.com')
        self.sent_email = SentEmail.objects.create(
            subject='Test Subject',
            body='Test Body',
            sender='sender@example.com',
            recipient='recipient@example.com',
            user=self.user
        )

    def test_str_representation(self):
        self.assertEqual(str(self.sent_email), 'Test Subject')
