# callanapp/management/commands/text_to_audio.py
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
import os
import shutil
from natsort import natsorted
import pygame
import time
from gtts import gTTS
import ffmpeg

from django.core.management.base import BaseCommand
from callanapp.forms import DictationForm  # Импортируйте вашу форму

class Command(BaseCommand):
    help = 'Convert text to audio and play it'

    def handle(self, *args, **options):
        # Получите данные из параметров
        #title_text = options['title_text']
        text = options['text']
        speed_factor = options['speed_factor']

        # Создайте экземпляр вашей формы и передайте данные в нее
        form_data = DictationForm({
            #'title_text': title_text,
            'text': text,
            'speed_factor': speed_factor,
        })

        # Проверьте валидность формы
        if form_data.is_valid():
            text = form_data.cleaned_data['text']
            speed_factor = form_data.cleaned_data['speed_factor']

            # Создайте временный аудиофайл из текста
            output_file_path = "temp_output.mp3"

            def change_audio_speed(input_path, output_path, speed_factor):
                ffmpeg.input(input_path).output(output_path, af=f'atempo={speed_factor}').run(overwrite_output=True)

            def create_audio(text, file_path):
                # Создаем объект gTTS
                tts = gTTS(text=text, lang='en', slow=True)
                # Сохраняем речь в аудиофайл
                tts.save(file_path)

            create_audio(text, output_file_path)

            def play_audio(file_path, repeat=2, pause_between_repeat=2):
                pygame.mixer.init()
                pygame.mixer.music.load(file_path)
                for _ in range(repeat):
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)
                    time.sleep(pause_between_repeat)

            # Загрузка аудиофайла
            audio = AudioSegment.from_file(output_file_path)

            # Увеличение чувствительности
            stripped_audio = detect_nonsilent(audio, silence_thresh=-45, min_silence_len=120)

            # Вывод информации о паузах
            print("Pauses:", stripped_audio)
            print(len(stripped_audio))

            # Разбивка аудио на дорожки между найденными паузами
            tracks = []
            for i, (start, end) in enumerate(stripped_audio):
                track = audio[start:end]
                tracks.append(track)

                # Создание папки output_folder, если её нет
                output_folder = "output_folder"
                os.makedirs(output_folder, exist_ok=True)

                # Сохранение дорожки в папку output_folder
                output_file_path = os.path.join(output_folder, f"output_track_{i}.mp3")
                track.export(output_file_path, format="mp3")

                print(f"Track {i} saved to {output_file_path}")

            # Получение списка файлов в папке
            track_files = os.listdir('output_folder')
            sorted_track_files = natsorted(track_files)

            print(sorted_track_files)

            # Объединение всех дорожек в одну
            audio = AudioSegment.empty()
            pause_duration = 3500  # Длительность паузы между дорожками в миллисекундах

            for track_file in sorted_track_files:
                # Полный путь к файлу
                track_path = os.path.join('output_folder', track_file)

                # Загрузка аудиодорожки
                track = AudioSegment.from_file(track_path)

                # Добавление каждой дорожки дважды с паузой между копиями
                audio += track
                audio += AudioSegment.silent(duration=pause_duration)
                audio += track
                audio += AudioSegment.silent(duration=pause_duration)

            # Сохранение результата
            output_audio_path = "output_audio.mp3"
            audio.export(output_audio_path, format="mp3")

            # Изменение скорости аудио
            new_output_path = "speed_changed.mp3"
            change_audio_speed(output_audio_path, new_output_path, speed_factor)

            print("Playing audio...")

            try:
                # Воспроизведение аудиофайла
                pygame.mixer.init()
                pygame.mixer.music.load(new_output_path)
                pygame.mixer.music.play()

                print("Audio playback started...")

                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)

                print("Audio playback finished.")
            except pygame.error as e:
                print(f"Error during audio playback: {e}")
            finally:
                # Освобождение памяти
                del audio, stripped_audio, tracks, track_files, sorted_track_files
                pygame.quit()

                # Удаление созданных папок и файлов
                shutil.rmtree('output_folder', ignore_errors=True)
                os.remove(output_audio_path)
                os.remove(new_output_path)
                os.remove('temp_output.mp3')

                print("Ресурсы освобождены, временные папки и файлы удалены")