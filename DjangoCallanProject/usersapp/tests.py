import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mynewsproject.settings')
from django.test import TestCase
from django.urls import reverse
from usersapp.models import BlogUser


class CapAppTests(TestCase):
    def setUp(self):
        self.user = BlogUser.objects.create_user(username='testuser', password='testpass')

    def test_authenticated_access(self):
        # Входим в систему под тестовым пользователем
        self.client.login(username='testuser', password='testpass')

        # Здесь размещаете код, который должен быть доступен только авторизованным пользователям
        response = self.client.get(reverse('usersapp:login'))
        self.assertEqual(response.status_code, 200)

    def test_unauthenticated_access(self):
        # Здесь размещаете код, который должен быть недоступен неавторизованным пользователям
        response = self.client.get(reverse('usersapp:register'))
        self.assertEqual(response.status_code, 200)


