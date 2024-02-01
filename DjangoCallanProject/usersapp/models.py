from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class BlogUser(AbstractUser):
    email = models.EmailField(unique=True)
    user = models.BooleanField(default=False)
    face_image = models.ImageField(upload_to='user_faces/', null=True, blank=True)

    # Переопределение метода save
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Создаем профиль
        # Если профиль не создан
        if not Profile.objects.filter(user=self).exists():
            Profile.objects.create(user=self)

# Модель профиля пользователя
class Profile(models.Model):
    info = models.TextField(blank=True)
    user = models.OneToOneField(BlogUser, on_delete=models.CASCADE)
    face_image = models.ImageField(upload_to='user_faces/', null=True, blank=True)
    # Дополнительные поля профиля, если необходимо

# Сигнал для создания профиля пользователя
@receiver(post_save, sender=BlogUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)





