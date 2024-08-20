from django.db import models
from django.utils.text import slugify

import sys
sys.path.append('../')
from users.models import *
sys.path.remove('../')

class Lobby(models.Model):
    user1 = models.ForeignKey(CustomUsers, models.CASCADE, related_name = "user1")
    user2 = models.ForeignKey(CustomUsers, models.CASCADE, related_name = "user2")
    is_user1_in = models.BooleanField(default=True, blank=True)
    is_user2_in = models.BooleanField(default=False, blank=True)
    lobby_name = models.SlugField(unique=True)
    message_history = models.TextField(blank=True)
    
    def save(self, *args, **kwargs):
        # Создаем слаг из ников пользователей, разделенных подчеркиванием
        self.lobby_name = slugify(f"{self.user1.slug}_{self.user2.slug}")
        super().save(*args, **kwargs)
    
class Games(models.Model):
    start_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    first_user = models.ForeignKey(CustomUsers, models.CASCADE, related_name = "first_user", null=True)
    score_first_user = models.PositiveIntegerField(default = 0)
    second_user = models.ForeignKey(CustomUsers, models.CASCADE, related_name = "second_user", null=True)
    score_second_user = models.PositiveIntegerField(default = 0)
    game_slug = models.SlugField()
    is_turn_first_user = models.BooleanField(default=True)
    
    winner = models.ForeignKey(CustomUsers, on_delete=models.CASCADE, related_name='winner', null=True)

    def save(self, *args, **kwargs):
        # Создаем слаг из ников пользователей, разделенных подчеркиванием
        self.game_slug = slugify(f"{self.first_user.slug}_{self.second_user.slug}")
        super().save(*args, **kwargs)

class Card(models.Model):
    RANK_CHOICES = [
        ('J', 'J'),
        ('Q', 'Q'),
        ('K', 'K'),
        ('A', 'A'),
    ]
    
    COLOR_CHOICES = [
        ('Black', 'Black'),
        ('Red', 'Red'),
    ]
    
    game = models.ForeignKey("Games", on_delete=models.CASCADE, related_name='cards')
    rank = models.CharField(max_length=1, choices=RANK_CHOICES)
    color = models.CharField(max_length=5, choices=COLOR_CHOICES)
    flipped = models.BooleanField(default=False)
    guessed = models.BooleanField(default=False)
    order = models.PositiveIntegerField()
    
    class Meta:
        unique_together = ['game', 'rank', 'color', 'order']