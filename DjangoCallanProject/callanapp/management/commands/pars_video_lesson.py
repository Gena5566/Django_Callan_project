from django.core.management.base import BaseCommand
import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from django.conf import settings

class Command(BaseCommand):
    help = 'Команда для парсинга видеоуроков'

    def handle(self, *args, **options):
        # Загрузите ваш JSON-файл с ключами доступа API
        json_file_path = os.path.join(settings.MEDIA_ROOT, 'hopeful-altar-412611-04b7e7cf18b5.json')
        credentials = Credentials.from_service_account_file(
            json_file_path, scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )

        # Создайте объект YouTube API
        youtube = build('youtube', 'v3', credentials=credentials)

        # Идентификатор канала @learningtime7512
        channel_id = 'UCRMOOrNi5hwmbbgYJbEc2wQ'

        try:
            # Получите список видео с канала
            request = youtube.channels().list(part='contentDetails', id=channel_id)
            response = request.execute()

            if 'items' in response and response['items']:
                playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

                # Получите информацию о видео из плейлиста
                request = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=10)
                response = request.execute()

                # Проверка наличия видео в плейлисте
                if 'items' in response and response['items']:
                    # Выведите информацию о каждом видео
                    for item in response['items']:
                        video_title = item['snippet']['title']
                        video_id = item['snippet']['resourceId']['videoId']
                        video_url = f'https://www.youtube.com/watch?v={video_id}'
                        self.stdout.write(self.style.SUCCESS(f'Title: {video_title}, URL: {video_url}'))
                else:
                    self.stdout.write(self.style.WARNING('Канал не содержит видео.'))
            else:
                self.stdout.write(self.style.WARNING(f'Не удалось получить информацию о канале {channel_id}.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ошибка при обработке данных YouTube: {e}'))



