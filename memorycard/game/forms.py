# from django import forms
# from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# from django.contrib.auth.models import User
# from captcha.fields import CaptchaField


# class RegisterUserForm(UserCreationForm):
#     username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'placeholder':"Логин"}))
#     email = forms.EmailField(label="Email", widget=forms.EmailInput({'placeholder':"Почта"}))
#     password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder':"Пароль"}))
#     password2 = forms.CharField(label="Повтор пароля", widget=forms.PasswordInput(attrs={'placeholder':"Повтор пароля"}))

#     captcha = CaptchaField()
#     class Meta:
#         model = User
#         fields = ('username','email', 'password1', 'password2')

# class LoginUserForm(AuthenticationForm):
#     username = forms.CharField(label="Логин", widget=forms.TextInput(attrs={'placeholder':"Логин"}))
#     password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder':"Пароль"}))

#     class Meta:
#         model = User
#         fields = ('username', 'password',)