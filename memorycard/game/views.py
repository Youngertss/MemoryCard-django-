from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.views.generic import ListView #, CreateView #, DetailView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, Page

import random
from .models import *
import sys
sys.path.append('../')
from users.forms import AvatarChangeForm
from users.models import *
sys.path.remove('../')

menu = [
    {'title': 'Быстрая игра', 'url_name':'play'},
    {'title': 'Друзья', 'url_name':'friends'},
    # {'title': 'Профиль', 'url_name':'profile'},
]

# Create your views here.
def index(request):
    return render(request, "game/index2.html", {'menu':menu})

def profile(request, user_slug):
    user = get_object_or_404(CustomUsers, slug=user_slug)
    context = {
        'menu':menu,
        'user':user,
    }
    
    return render(request, "game/profile.html", context)

def change_avatar(request):
    if request.method == 'POST':
        form = AvatarChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            # Обработка успешного сохранения, например, редирект на профиль пользователя
            return redirect("profile", user_slug = request.user.slug)
    else:
        form = AvatarChangeForm(instance=request.user)
    
    return render(request, 'game/change_avatar.html', {'form': form})

def all_users(request):
    users = CustomUsers.objects.all()

    paginator = Paginator(users, 5)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "menu":menu, 
        "user_name":"", 
        "page_obj": page_obj,
    }
    
    return render(request, "game/all_users.html", context)

def friends(request):
    users = request.user.friends.all()

    paginator = Paginator(users, 5)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "menu":menu, 
        "user_name":"", 
        "page_obj": page_obj,
    }
    
    return render(request, "game/friends.html", context)

def sent_friends(request):
    users = request.user.friend_requests_sent.all()

    paginator = Paginator(users, 5)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "menu":menu, 
        "user_name":"", 
        "page_obj": page_obj,
    }
    
    return render(request, "game/sent_friends.html", context)

def received_friends(request):
    users = request.user.sent_friend_requests.all()

    paginator = Paginator(users, 5)
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "menu":menu, 
        "user_name":"", 
        "page_obj": page_obj,
    }
    
    return render(request, "game/received_friends.html", context)


def friends__find(request, user_name):
    context = {"menu":menu, "user_name":user_name}
    if user_name:
        try:
            user_find = CustomUsers.objects.get(username=user_name)
        except CustomUsers.DoesNotExist:
            user_find = None
        context["user_find"] = user_find
    else:
        context["user_find"] = None
    return render(request, "game/friends.html", context)


def play(request):
    return HttpResponse("играть")


def game_starting(request, userslug1, userslug2):
    # Получите пользователей на основе их slug (замените эту часть кода на свою логику)
    user1 = CustomUsers.objects.get(slug=userslug1)
    user2 = CustomUsers.objects.get(slug=userslug2)

    # Создайте новую игру
    new_game, created = Games.objects.get_or_create(first_user=user1, second_user=user2)
    print(created, "-----------------------VIEWS GAME_STARTING")
    if created:
        # Генерация 16 карточек
        ranks = ['J', 'J', 'Q', 'Q', 'K', 'K', 'A', 'A']
        colors = ['Black', 'Red']
        all_cards = []

        for rank in ranks:
            for color in colors:
                all_cards.append({'rank': rank, 'color': color})

        random.shuffle(all_cards)

        for order, card_data in enumerate(all_cards, start=1):
            Card.objects.create(
                game=new_game,
                rank=card_data['rank'],
                color=card_data['color'],
                order=order
            )

    # Определите значения контекста
    # context = {
    #     'first_user': user1.username,
    #     'second_user': user2.username,
    #     'is_turn_first_user': new_game.is_turn_first_user,  # Установите начальное значение
    #     'cards': new_game.cards.all(),  # Получите все карточки для этой игры
    # }

    return render(request, "index.html", )
#лобби ожидания и создание его
def play_lobby(request, userslug1, userslug2):
    user1 = get_object_or_404(CustomUsers, slug=userslug1)
    user2 = get_object_or_404(CustomUsers, slug=userslug2)

    if request.user == user2:
        user1.play_requests_sent.remove(user2)
    
    #берем лобби либо создаем его
    curr_lobby, created = Lobby.objects.get_or_create(user1=user1, user2=user2)
    lobby_name = curr_lobby.lobby_name
    nick1, nick2 = lobby_name.split('_')
    context = {
        'menu':menu, 
        'lobby_name':lobby_name, 
        'nick1':nick1, 
        'nick2':nick2
    }
    return render(request, 'game/play_lobby.html', context)

#предложение играть
def send_play_request(request, friend_id):
    sender_profile = get_object_or_404(CustomUsers, slug=request.user.slug) 
    recipient_profile = get_object_or_404(CustomUsers, id=friend_id)

    sender_profile.play_requests_sent.add(recipient_profile) #"Отправил ему запросс"
    
    #Cоздать лобби и перейти в него
    userslug1 = sender_profile.slug
    userslug2 = recipient_profile.slug
    return redirect('play_lobby', userslug1=userslug1, userslug2=userslug2)

#отклонения плредложения играть
def reject_play_request(request, friend_id):
    recipient_profile = get_object_or_404(CustomUsers, username=request.user)
    sender_profile = get_object_or_404(CustomUsers, id=friend_id)

    if recipient_profile in sender_profile.play_requests_sent.all():
        sender_profile.play_requests_sent.remove(recipient_profile) #"Удлил отправленный ему запросс"

        #Обновить страничку(заново перейти на нее)
        url_to = sender_profile.get_absolute_url()
        return redirect(url_to)
    else:
        return HttpResponse("No friend request found!")
    

#отправить запрос в друзья
def send_friend_request(request, friend_id):
    sender_profile = get_object_or_404(CustomUsers, username=request.user) 
    recipient_profile = get_object_or_404(CustomUsers, id=friend_id)

    sender_profile.friend_requests_sent.add(recipient_profile) #"Отправил ему запросс"
    
    #Обновить страничку(заново перейти на нее)
    url_to = recipient_profile.get_absolute_url()
    return redirect(url_to)
    

def accept_friend_request(request, friend_id):
    recipient_profile = get_object_or_404(CustomUsers, username=request.user)
    sender_profile = get_object_or_404(CustomUsers, id=friend_id)

    if recipient_profile in sender_profile.friend_requests_sent.all():
        sender_profile.friend_requests_sent.remove(recipient_profile) #"Удлил отправленный ему запросс"
        
        #Добавление в друзья
        recipient_profile.friends.add(sender_profile)
        sender_profile.friends.add(recipient_profile)
        
        #Обновить страничку(заново перейти на нее)
        url_to = sender_profile.get_absolute_url()
        return redirect(url_to)
    else:
        return HttpResponse("No friend request found!")

def reject_friend_request(request, friend_id):
    recipient_profile = get_object_or_404(CustomUsers, username=request.user)
    sender_profile = get_object_or_404(CustomUsers, id=friend_id)

    if recipient_profile in sender_profile.friend_requests_sent.all():
        sender_profile.friend_requests_sent.remove(recipient_profile) #"Удлил отправленный ему запросс"

        #Обновить страничку(заново перейти на нее)
        url_to = sender_profile.get_absolute_url()
        return redirect(url_to)
    else:
        return HttpResponse("No friend request found!")
# def registering(request):
#     return render(request, "game/registering.html", {'menu':menu})

