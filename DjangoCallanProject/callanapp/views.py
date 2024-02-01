from django.shortcuts import render, get_object_or_404, HttpResponseRedirect, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .management.commands.text_to_audio import Command
from .models import Word, AudioDictation, SentEmail
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from .forms import ContactForm, ReplyEmailForm
from django.shortcuts import reverse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
import os
from django.utils.decorators import method_decorator
from django.contrib import messages
import logging
from googleapiclient.discovery import build
from google.oauth2 import service_account
from django.shortcuts import render
import json
from django.views.decorators.cache import cache_page





logger = logging.getLogger(__name__)




# Базовый класс для представлений с общими методами
class BaseView(View):
    template_name = ''

    @method_decorator(login_required)
    def get(self, request):
        """Обработка GET-запроса."""
        return render(request, self.template_name)


class IndexView(BaseView):
    template_name = 'callanapp/index.html'




class Dictation_to_text(BaseView):
    template_name = 'callanapp/dictation_to_text.html'


    @staticmethod
    @csrf_exempt
    def convert_and_play(request):
        """Конвертация текста в аудио и воспроизведение."""
        if request.method == 'POST':
            try:
                text = request.POST['text']
                speed_factor = float(request.POST['speed_factor'])
                command = Command()
                command.handle(text=text, speed_factor=speed_factor)

                # Путь к созданному аудиофайлу
                new_output_path = os.path.join(settings.MEDIA_ROOT, 'speed_changed.mp3')
                audio_url = request.build_absolute_uri(settings.MEDIA_URL + 'speed_changed.mp3')

                return JsonResponse({'status': 'success', 'audio_url': audio_url})
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e), 'code': e.code})
        return JsonResponse({'status': 'error', 'message': 'Недопустимый метод запроса'})


class SearchAudioDictations(BaseView):
    template_name = 'callanapp/dictation_stage.html'


    def search_audio_dictations(self):
        """Поиск аудиодиктантов по уровню."""
        try:
            stage = self.GET.get('stage')
            audio_dictations = self.get_audio_dictations(stage)
            result = self.get_audio_dictation_info(audio_dictations)
            return JsonResponse({'status': 'success', 'audio_dictations': result})
        except ValidationError as e:
            return JsonResponse({'status': 'error', 'message': str(e), 'code': e.code})


    def get_audio_dictations(self, stage):
        """Получение аудиодиктантов по уровню."""
        return AudioDictation.objects.filter(stage__exact=stage)

    def get_audio_dictation_info(self, audio_dictations):
        """Получение информации об аудиодиктантах."""
        result = []
        for audio_dictation in audio_dictations:
            audio_url = audio_dictation.audio_dictation.url
            result.append({
                'stage': audio_dictation.stage,
                'title_text_user': audio_dictation.title_text_user,
                'text_user': audio_dictation.text_user,
                'audio_url': audio_url,
            })
        return result


class DeleteAudioFileView(BaseView):
    def post(self, request):
        """Удаление аудиофайла."""
        try:
            file_name = 'speed_changed.mp3'
            self.delete_audio_file(file_name)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    def delete_audio_file(self, file_name):
        """Удаление аудиофайла из хранилища Django."""
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        os.remove(file_path)


class WordView(BaseView):
    template_name = 'callanapp/select_stage_word.html'


class WordQuiz(BaseView):
    template_name = 'callanapp/quiz.html'

    def get(self, request):
        """Отображение викторины по словам."""
        words = list(Word.objects.all())
        context = {'words': words}
        return render(request, self.template_name, context)

    def post(self, request):
        """Обработка ответов пользователя в викторине по словам."""
        words = list(Word.objects.all())
        score, user_answers = self.calculate_score_and_answers(words, request)
        context = {
            'words': words,
            'score': score,
            'user_answers': user_answers,
            'is_correct': [is_correct for word, is_correct in zip(words, user_answers.values())],
        }
        return render(request, self.template_name, context)

    def calculate_score_and_answers(self, words, request):
        """Вычисление баллов и ответов пользователя."""
        score = 0
        user_answers = {}
        for word in words:
            user_translation = request.POST.get(word.russian_word)
            user_answers[word.russian_word] = user_translation
            expected_translation = word.english_translation.lower()
            is_correct = user_translation and user_translation.lower() == expected_translation
            score += 1 if is_correct else 0
        return score, user_answers


class ReadBook(BaseView):
    template_name = 'callanapp/read_student_book.html'


class Contact(BaseView):
    template_name = 'callanapp/contact.html'

    def get(self, request):
        """Отображение формы контактов."""
        form = ContactForm()
        return render(request, self.template_name, context={'form': form})

    def post(self, request):
        """Обработка отправки формы контактов."""
        form = ContactForm(request.POST)
        if form.is_valid():
            name, message, email = self.extract_form_data(form)
            self.send_contact_email(message, email)
            return HttpResponseRedirect(reverse('index'))
        else:
            return render(request, self.template_name, context={'form': form})

    def extract_form_data(self, form):
        """Извлечение данных из формы контактов."""
        return form.cleaned_data['name'], form.cleaned_data['message'], form.cleaned_data['email']

    def send_contact_email(self, message, email):
        """Отправка уведомления о получении сообщения."""
        email_subject = 'Contact message'
        email_body = f'Your message: {message}\n\n\nYour message has been received. Thank you!'
        try:
            send_mail(
                email_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            SentEmail.objects.create(
                subject=email_subject,
                body=email_body,
                sender=settings.DEFAULT_FROM_EMAIL,
                recipient=email,
            )
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
        else:
            logger.info("Email sent successfully!")


class ReplyEmailView(BaseView):
    template_name = 'admin/reply_email.html'

    def get(self, request, email_id):
        """Обработка GET-запроса при ответе на электронное письмо."""
        email = self.get_sent_email_or_404(email_id)
        return render(request, self.template_name, {'email': email, 'form': ReplyEmailForm()})

    def post(self, request, email_id):
        """Обработка POST-запроса при отправке ответа на электронное письмо."""
        email = self.get_sent_email_or_404(email_id)
        recipient = email.sender
        form = ReplyEmailForm(request.POST)
        if form.is_valid():
            subject, body = self.extract_form_data(form)
            self.send_reply_email(subject, body, recipient)
            return self.redirect_with_success_message(request, 'Email sent successfully.')
        else:
            return self.redirect_with_error_message(request, 'Invalid form submission. Please check the form.')

    def get_sent_email_or_404(self, email_id):
        """Получение объекта SentEmail или 404."""
        return get_object_or_404(SentEmail, id=email_id)

    def extract_form_data(self, form):
        """Извлечение данных из формы ответа на электронное письмо."""
        return form.cleaned_data['subject'], form.cleaned_data['body']

    def send_reply_email(self, subject, body, recipient):
        """Отправка ответного электронного письма."""
        try:
            send_mail(
                subject,
                body,
                'admin@example.com',
                [recipient],
                fail_silently=False,
            )
            messages.success(request, 'Email sent successfully.')
        except Exception as e:
            messages.error(request, f'Failed to send email: {e}')

    def redirect_with_success_message(self, request, message):
        """Перенаправление с сообщением об успешной операции."""
        messages.success(request, message)
        return redirect('admin:sentemail_changelist')

    def redirect_with_error_message(self, request, message):
        """Перенаправление с сообщением об ошибке."""
        messages.error(request, message)
        return redirect('admin:sentemail_changelist')






# Класс для отображения видеоматериалов с YouTube
@method_decorator(cache_page(60 * 30), name='dispatch') # Кэшировать страницу на 30 минут
class YouTubeDataFetcher(BaseView):
    template_name = 'callanapp/youtube_videos.html'

    def __init__(self):
        # Здесь необходимо подставить путь к вашему файлу JSON
        path_to_json_file = os.path.join(settings.MEDIA_ROOT, 'hopeful-altar-412611-04b7e7cf18b5.json')

        with open(path_to_json_file, 'r') as json_file:
            service_account_info = json.load(json_file)

        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def get(self, request):
        channel_id = 'UCRMOOrNi5hwmbbgYJbEc2wQ'  # Замените на свой channel_id
        playlist_info = self.get_playlist_info(channel_id)

        return render(request, self.template_name, playlist_info)

    def get_playlist_info(self, channel_id):
        try:
            response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()

            playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            videos = self.get_videos_from_playlist(playlist_id)
        except KeyError as e:
            logger.error('Ошибка при получении данных YouTube: %s', e)
            return {'error_message': 'Не удалось получить информацию о канале'}

        return {'videos': videos}

    def get_videos_from_playlist(self, playlist_id):
        videos = []
        next_page_token = None

        while True:
            response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in response.get('items', []):
                video_title_full = item['snippet']['title']

                # Оставляем только часть с названием урока
                video_title, _, _ = video_title_full.partition('#')

                video_id = item['snippet']['resourceId']['videoId']
                video_url = f'https://www.youtube.com/embed/{video_id}'

                videos.append({'title': video_title, 'url': video_url})
                print('title:', video_title)
                print('url:', video_url)

            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return videos



# Класс для отображения видеоматериалов с YouTube в виде списка
@method_decorator(cache_page(60 * 30), name='dispatch') # Кэшировать страницу на 30 минут
class YouTubeDataList(BaseView):
    template_name = 'callanapp/list_of_video_files.html'

    def __init__(self):
        # Здесь необходимо подставить путь к вашему файлу JSON
        path_to_json_file = os.path.join(settings.MEDIA_ROOT, 'hopeful-altar-412611-04b7e7cf18b5.json')

        with open(path_to_json_file, 'r') as json_file:
            service_account_info = json.load(json_file)

        self.credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def get(self, request):
        channel_id = 'UCRMOOrNi5hwmbbgYJbEc2wQ'  # Замените на свой channel_id
        playlist_info = self.get_playlist_info(channel_id)

        return render(request, self.template_name, playlist_info)

    def get_playlist_info(self, channel_id):
        try:
            response = self.youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()

            playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

            videos = self.get_videos_from_playlist(playlist_id)
        except KeyError as e:
            logger.error('Ошибка при получении данных YouTube: %s', e)
            return {'error_message': 'Не удалось получить информацию о канале'}

        return {'videos': videos}

    def get_videos_from_playlist(self, playlist_id):
        videos = []
        next_page_token = None

        while True:
            response = self.youtube.playlistItems().list(
                part='snippet',
                playlistId=playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in response.get('items', []):
                video_title_full = item['snippet']['title']

                # Оставляем только часть с названием урока
                video_title, _, _ = video_title_full.partition('#')

                video_id = item['snippet']['resourceId']['videoId']
                video_url = f'https://www.youtube.com/embed/{video_id}'

                videos.append({'title': video_title, 'url': video_url})
                print('title:', video_title)
                print('url:', video_url)

            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return videos