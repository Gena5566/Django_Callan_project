from django.urls import path, include
from callanapp import views
from .views import IndexView
from django.conf import settings
from django.conf.urls.static import static
from .views import Dictation_to_text, WordQuiz, WordView, DeleteAudioFileView, ReadBook, SearchAudioDictations, Contact, ReplyEmailView, YouTubeDataFetcher, YouTubeDataList
from django.contrib import admin

admin.autodiscover()

urlpatterns = [
    path('', IndexView.as_view(), name='index'),  # Главная страница
    path('dictation_to_text/', Dictation_to_text.as_view(), name='dictation_to_text'),  # URL-маршрут для преобразования текста в аудио
    path('convert_and_play/', Dictation_to_text.convert_and_play, name='convert_and_play'),  # URL-маршрут для преобразования текста и проигрывания
    path('delete_audio_file/', DeleteAudioFileView.as_view(), name='delete_audio_file'),  # URL-маршрут для удаления аудиофайла
    path('select_stage_word/', WordView.as_view(), name='select_stage_word'),  # URL-маршрут для выбора уровня слова
    path('word_quiz/', WordQuiz.as_view(), name='word_quiz'),  # URL-маршрут для викторины по словам
    path('audio_url/', Dictation_to_text.convert_and_play, name='audio_url'),  # URL-маршрут для получения аудио-URL
    path('read_student_book/', ReadBook.as_view(), name='read_student_book'),  # URL-маршрут для чтения книги студента
    path('dictation_stage/', SearchAudioDictations.as_view(), name='dictation_stage'),  # URL-маршрут для поиска аудио-диктантов
    path('search_audio_dictations/', SearchAudioDictations.search_audio_dictations, name='search_audio_dictations'),  # URL-маршрут для выполнения поиска аудио-диктантов
    path('contact/', Contact.as_view(), name='contact'),  # URL-маршрут для страницы контактов
    # path('admin/sentemail/<int:email_id>/reply/', ReplyEmailView.as_view(), name='admin_sentemail_reply'),  # URL-маршрут для ответа на электронное письмо из административной панели
    path('sentemail/<int:email_id>/reply/', ReplyEmailView.as_view(), name='admin_sentemail_reply'),  # URL-маршрут для ответа на электронное письмо
    path('youtube_videos/', YouTubeDataFetcher.as_view(), name='youtube_videos'), # URL-маршрут для видеофайлов
    path('list_of_video_files/', YouTubeDataList.as_view(), name='list_of_video_files'), # URL-маршрут для видеофайлов в виде списка
]

# Добавляем статические маршруты для обслуживания медиафайлов только в режиме DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
