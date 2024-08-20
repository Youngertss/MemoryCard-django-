from django.urls import path, re_path

from .views import *

urlpatterns = [
    # path('profile/', profile, name='profile'),
    path('login/', LoginUser.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('registering/', RegisterUser.as_view(), name='registering'),
]

