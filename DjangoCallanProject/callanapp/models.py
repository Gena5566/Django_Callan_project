# models.py
from django.db import models
from usersapp.models import BlogUser

# Менеджер для фильтрации только активных объектов
class ActiveManager(models.Manager):
    def get_queryset(self):
        all_objects = super().get_queryset()
        return all_objects.filter(is_active=True)

# Базовая абстрактная модель для общих полей
class BaseModel(models.Model):
    title_text_user = models.CharField(max_length=20)
    text_user = models.TextField(null=True, blank=True)
    audio_dictation = models.FileField(upload_to='audio/')

    class Meta:
        abstract = True  # Абстрактная модель, не создает отдельной таблицы в базе данных

    def __str__(self):
        return self.title_text_user  # Строковое представление объекта

# Модель для аудиодиктантов, наследующаяся от BaseModel
class AudioDictation(BaseModel):
    stage = models.IntegerField()

    def __str__(self):
        return f'{self.stage} - {self.title_text_user} - {self.text_user} - {self.audio_dictation}'

# Модель для хранения слов
class Word(models.Model):
    LEVEL_CHOICES = [
        ('Stage 1', 'Stage 1'),
        ('Stage 2', 'Stage 2'),
        ('Stage 3', 'Stage 3'),
        ('Stage 4', 'Stage 4'),
        # Добавьте остальные уровни по мере необходимости
    ]

    russian_word = models.CharField(max_length=255)
    english_translation = models.CharField(max_length=255)
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES)

    def __str__(self):
        return f'{self.russian_word} ({self.level})'

# Модель для хранения отправленных электронных писем
class SentEmail(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    sender = models.EmailField()
    recipient = models.EmailField()
    sent_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(BlogUser, on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.subject
