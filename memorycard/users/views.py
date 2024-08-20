
from django.shortcuts import redirect
from django.contrib.auth import login, logout
from django.views.generic import CreateView #, ListView, DetailView
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import *

# Create your views here.
menu = [
    {'title': 'Быстрая игра', 'url_name':'play'},
    {'title': 'Друзья', 'url_name':'friends'},
    # {'title': 'Профиль', 'url_name':'profile'},
]

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'game/registering.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        return context
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'game/login.html'
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['menu'] = menu
        return context
    
    def get_success_url(self):
        return reverse_lazy('home')

def logout_user(request):
    logout(request)
    return redirect('login')
