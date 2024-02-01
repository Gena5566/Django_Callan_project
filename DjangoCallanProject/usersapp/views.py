from django.contrib.auth.views import LoginView
from django.shortcuts import get_object_or_404
from django.shortcuts import render, HttpResponseRedirect, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.conf import settings
from .forms import RegistrationForm
from django.views.generic import CreateView, DetailView, FormView, View
from .models import BlogUser
from rest_framework.authtoken.models import Token
from .forms import CustomAuthenticationForm
from django.utils.decorators import method_decorator
from PIL import Image
import logging
import os
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login, logout

from usersapp.models import BlogUser, Profile
from usersapp.forms import CustomAuthenticationForm



logger = logging.getLogger(__name__)






class UserLoginView(LoginView):
    template_name = 'usersapp/login.html'






@method_decorator(csrf_exempt, name='dispatch')
class CustomAuthenticationView(View):
    template_name = 'usersapp/login_face.html'


    def get(self, request, *args, **kwargs):
        form = CustomAuthenticationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        return self.receive_username(request)


    def receive_username(self, request):

        username = request.POST.get('username', None)

        user = get_object_or_404(BlogUser, username=username)
        login(self.request, user)
        print('Имя пользователя:', user)

        if user and user.face_image:
            photo_url = user.face_image.url
            print('URL photo:', photo_url)
        else:
            photo_url = None

        # Получить полный путь к файлу
        file_path = photo_url.split('/')[-1]
        print('путь к файлу:', file_path)

        # Проверить существование файла
        print("Содержимое директории:", os.listdir(settings.MEDIA_ROOT))

        filename = os.path.join(settings.MEDIA_ROOT, 'user_faces', file_path)
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found: {}".format(filename))

        file_type = os.path.splitext(filename)[1]
        file_size = os.path.getsize(filename)

        print(f"Тип файла: {file_type}")
        print(f"Размер файла: {file_size} байт")

        # Загрузите изображение
        image = Image.open(filename)

        # Отобразите изображение
        image.show()


        # Устанавливаем Content-Type в application/json
        response_data = {'status': 'success', 'message': 'Имя успешно получено'}
        return JsonResponse(response_data)




class UserCreateView(CreateView):
    model = BlogUser
    template_name = 'usersapp/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('users:login')


    def form_valid(self, form):
        # Дополнительные действия перед сохранением формы
        username = form.cleaned_data['username']  # Получаем значение 'username' из формы
        face_image = self.request.FILES['face_image']

        # Создаем имя файла, добавляя 'username' к 'face_image'
        filename = f"face_image_{username}.{face_image.name.split('.')[-1]}"

        # Присваиваем новое имя файлу
        form.cleaned_data['face_image'].name = filename

        # Ваш код обработки изображения, если это необходимо

        # Передача управления родительскому методу для сохранения формы
        return super().form_valid(form)



class UserDetailView(DetailView):
    template_name = 'usersapp/profile.html'
    model = BlogUser

    def get_object(self, queryset=None):
        return self.request.user



def update_token(request):
    user = request.user
    # если уже есть
    if user.auth_token:
        # обновить
        user.auth_token.delete()
        Token.objects.create(user=user)
    else:
        # создать
        Token.objects.create(user=user)
    return HttpResponseRedirect(reverse('users:profile', kwargs={'pk': user.pk}))

def update_token_ajax(request):
    user = request.user
    # если уже есть
    if user.auth_token:
        # обновить
        user.auth_token.delete()
        token = Token.objects.create(user=user)
    else:
        # создать
        token = Token.objects.create(user=user)
    return JsonResponse({'key': token.key})



def receive_face(request):
    logging.info("Функция приема изображения запущена")

    if request.method == 'POST':
        try:
            # Получаем данные изображения из тела запроса
            photo_data = request.FILES.get('photo_data')

            # Получить тип данных
            content_type = photo_data.content_type
            # Получить размер данных
            size = photo_data.size

            # Вывести тип и размер данных
            print("Тип данных:", content_type)
            print("Размер данных:", size)

            # Открыть изображение
            image = Image.open(photo_data)

            # Отобразите изображение
            image.show()



            # Возвращаем успешный JSON-ответ
            return JsonResponse({'status': 'success', 'message': 'Image successfully received'})

        except Exception as e:
            # Логируем ошибку
            logging.error(f"Error processing image: {e}")

    # Логируем некорректный запрос
    logging.warning("Invalid request received")

    # Вернуть JSON-ответ с ошибкой в случае некорректного запроса
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})













