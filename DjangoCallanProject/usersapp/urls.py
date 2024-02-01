# DjangoCallanProject/usersapp/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import CustomAuthenticationView

app_name = 'usersapp'

urlpatterns = [
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('login_face/', CustomAuthenticationView.as_view(), name='login_face'),

    path('receive_username/', CustomAuthenticationView.as_view(), name='receive_username'),  # URL-маршрут для передачи имени пользователя
    #path('receive_face/', CustomAuthenticationView.as_view(), name='receive_face'),# URL-маршрут для передачи фото
    path('receive_face/', views.receive_face , name='receive_face'),

    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.UserCreateView.as_view(), name='register'),
    path('profile/<int:pk>/', views.UserDetailView.as_view(), name='profile'),
    path('profile/', views.UserDetailView.as_view(), name='profile_no_pk'),
    path('update_token/', views.update_token, name='update_token'),
    path('update_token_ajax/', views.update_token_ajax),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


