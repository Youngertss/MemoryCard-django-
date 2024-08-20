from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from captcha.fields import CaptchaField
from django.utils.text import slugify

from .models import CustomUsers

class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'placeholder':"Логин"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput({'placeholder':"Почта"}))
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder':"Пароль"}))
    password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'placeholder':"Повтор пароля"}))

    captcha = CaptchaField()
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.slug = slugify(self.cleaned_data['username'])
        if commit:
            user.save()
        return user
    
    class Meta:
        model = CustomUsers
        fields = ('username','email', 'password1', 'password2')

class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'placeholder':"Логин"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder':"Пароль"}))

    class Meta:
        model = CustomUsers
        fields = ('username', 'password',)

class AvatarChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUsers
        fields = ['photo']