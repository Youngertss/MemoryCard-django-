from django.urls import path, re_path

from .views import *

urlpatterns = [
    path("", index, name='home'),
    path('change_avatar/', change_avatar, name='change_avatar'),
    path('play/', play, name='play'),
    path('play/<slug:userslug1>/<slug:userslug2>/', play_lobby, name='play_lobby'),
    path('send_play_request/<int:friend_id>/', send_play_request, name='send_play_request'),
    path('reject_play_request/<int:friend_id>/', reject_play_request, name='reject_play_request'),
    
    path('play/<slug:userslug1>/<slug:userslug2>/start/', game_starting, name='game_starting'),
    
    path('all_users/', all_users, name='all_users'),
    path('friends/', friends, name='friends'),
    path('sent_friends/', sent_friends, name='sent_friends'),
    path('received_friends/', received_friends, name='received_friends'),
    
    path('friends/<slug:user_name>/', friends__find, name='friends_find'),
    path('profile/<slug:user_slug>/', profile, name='profile'),
    
    path('send_friend_request/<int:friend_id>/', send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:friend_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:friend_id>/', reject_friend_request, name='reject_friend_request'),
    
    
    # path('login/', LoginUser.as_view(), name='login'),
    # path('logout/', logout_user, name='logout'),
    # path('registering/', RegisterUser.as_view(), name='registering'),
]

from django.conf.urls.static import static
from memorycard import settings

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)