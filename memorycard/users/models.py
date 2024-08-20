from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.urls import reverse
from django.utils.text import slugify
# Create your models here.

class CustomUsers(AbstractUser):
    username = models.CharField(max_length=60, unique=True, null=True, blank=True, validators=[
        RegexValidator(
            regex=r'^[a-zA-Z0-9_-]+$',
            message='Никнейм может содержать только английские буквы, цифры, знаки "-" и "_"'
        ),
    ])
    slug = models.SlugField(unique=True, blank=True)
    games = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    photo = models.ImageField(upload_to="photos/%Y/%m/%d/", default="")
    friend_requests_sent = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="sent_friend_requests")
    play_requests_sent = models.ManyToManyField('self', blank=True, symmetrical=False, related_name="play_sent_requests")
    friends = models.ManyToManyField('self', blank=True)
    
    class Meta:
        unique_together = ('username', 'slug')

    def get_absolute_url(self):
        return reverse('profile', kwargs={'user_slug': self.slug})