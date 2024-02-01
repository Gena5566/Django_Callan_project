import cv2
from django.core.management.base import BaseCommand
from django.http import StreamingHttpResponse
import threading
import dlib
from django.contrib.auth.views import LoginView
from django.http import HttpResponse


class Command(BaseCommand):
    help = 'Run face recognition video stream'

    def handle(self, *args, **options):
        cap = cv2.VideoCapture(0)
        print('Камера подключена')

        streaming = True  # Добавлен флаг streaming

        while streaming:
            ret, frame = cap.read()

            if ret:
                # Добавим вывод кадра в консоль для отладки
                print("New frame received:", frame)

                face = face_recognition(frame)
                print("Detected face coordinates:", face)

                if face is not None:
                    top, left, bottom, right = face
                    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

                data = cv2.imencode(".jpg", frame)[1].tostring()
                response = StreamingHttpResponse(data)

                response['Content-Type'] = 'image/jpeg'
                response['Content-Length'] = len(data)

                yield response  # Изменил return на yield

        cap.release()
        cv2.destroyAllWindows()


def face_recognition(frame):
    # Создаем детектор лиц
    face_detector = dlib.get_frontal_face_detector()
    # Преобразуем кадр в оттенки серого
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Ищем лица на кадре
    faces = face_detector(gray_frame)

    # Если найдено лицо, возвращаем его координаты
    if faces:
        face = faces[0]
        return face.top(), face.right(), face.bottom(), face.left()
    else:
        return (0, 0, 0, 0)  # Возвращаем координаты "лица" (0, 0, 0, 0) в случае, если лицо не обнаружено


class UserLoginView(LoginView):
    template_name = 'usersapp/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получить CSRF-токен
        csrf_token = get_token(self.request)

        # Получить видеопоток с камеры
        video_stream_url = 'http://localhost:8001/video_stream/'  # Обновите этот URL, если необходимо
        try:
            response = requests.get(video_stream_url, stream=True, headers={'X-CSRFToken': csrf_token})
            context['video_stream'] = f"data:image/jpeg;base64,{response.content.decode('utf-8')}"
        except requests.RequestException as e:
            print(f"Ошибка при получении видеопотока: {e}")
            context['video_stream'] = None

        return context














