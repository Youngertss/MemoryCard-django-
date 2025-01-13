from django.test import TestCase
import sys
sys.path.append('../')
from users.models import *
sys.path.remove('../')

# Create your tests here.
class TestGame(TestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        CustomUsers.objects.create(username="Pupsen", slug="pupsen", email="pupsen@gmail.com")
        CustomUsers.objects.create(username="Botyara", slug="botyara", email="botyara@gmail.com", is_bot=True)
        
    def test_withbot_game(self):
        response = self.client.get("/play_withbot/pupsen/botyara/start/")
        self.assertEqual(response.status_code, 200)
    
    def test_index(self):
        response = self.client.get("")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Быстрая игра", response.content.decode())
        