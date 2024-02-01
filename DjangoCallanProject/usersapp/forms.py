from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import BlogUser
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate

class RegistrationForm(UserCreationForm):
    # Поле для изображения
    face_image = forms.ImageField(label='Для регистрации используйте сохраненное фото ', required=False, widget=forms.FileInput(attrs={'id': 'id_face_image'}))

    class Meta:
        model = BlogUser
        fields = ['username', 'password1', 'password2', 'email', 'face_image']





class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')

        return cleaned_data

