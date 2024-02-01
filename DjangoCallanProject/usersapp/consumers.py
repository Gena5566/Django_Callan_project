import json
import array
import base64
import logging
import cv2
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.files.storage import default_storage
import dlib

logger = logging.getLogger(__name__)

# Создаем детектор лиц
face_detector = dlib.get_frontal_face_detector()

class VideoConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.face_detected = False

    async def connect(self):
        logger.info('WebSocket connection established.')
        await self.accept()

    async def disconnect(self, close_code):
        logger.info('WebSocket connection closed.')

    async def receive(self, bytes_data, **kwargs):
        try:
            logger.info(f'Received bytes data: {bytes_data[:50]}...')  # Логируем первые 50 байт полученных данных
            image_blob = bytearray(array.array('B', bytes_data))

            if image_blob:
                logger.info(f'Type of image_blob: {type(image_blob)}')
                logger.info(f'Size of image_blob: {len(image_blob)} bytes')

                # Сохранение видео
                video_path = await self.save_video_from_blob(image_blob)

                # Передача видео на обработку
                await self.process_video(video_path)

        except Exception as e:
            logger.error(f'Error: {e}')
            await self.send_error_notification(f'Error: {e}')

    async def save_video_from_blob(self, image_blob):
        try:
            video_path = 'video_stream.avi'
            with default_storage.open(video_path, 'wb') as video_file:
                video_file.write(image_blob)

                full_path = default_storage.path(video_path)
                logger.info(f'Saved video to: {full_path}')
                return full_path

        except Exception as e:
            logger.error(f'Error saving video file: {e}')
            return None

    async def process_video(self, video_path):
        try:
            cap = cv2.VideoCapture(video_path)

            while cap.isOpened():
                ret, frame = cap.read()

                if ret:
                    # Обработка кадра
                    detected_faces = await self.face_recognition(frame)

                    # Вывод координат рамок в терминал и сохранение изображения с рамкой
                    if detected_faces and not self.face_detected:
                        self.face_detected = True
                        logger.info(f'Detected face coordinates: {detected_faces[0]}')
                        await self.save_frame_with_face(frame)

                        # Отправка обработанного кадра клиенту
                        await self.send_processed_frame('frame_with_face.png')  # Указываем путь к изображению с лицом

                else:
                    break

            cap.release()

        except Exception as e:
            logger.error(f'Error processing video: {e}')

    async def face_recognition(self, frame):
        try:
            # Преобразуем кадр в оттенки серого
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Ищем лица на кадре
            faces = face_detector(gray_frame)

            detected_faces = []

            # Если на кадре найдено лицо, возвращаем его координаты
            for face in faces:
                top, right, bottom, left = face.top(), face.right(), face.bottom(), face.left()
                cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)
                detected_faces.append((top, right, bottom, left))

            #logger.info(f'Detected faces: {len(detected_faces)}')
            return detected_faces

        except Exception as e:
            logger.error(f'Error in face recognition: {e}')
            return []

    async def save_frame_with_face(self, frame):
        try:
            # Сохранение кадра с лицом
            saved_frame_path = 'frame_with_face.png'
            cv2.imwrite(saved_frame_path, frame)
            logger.info(f'Saved frame with detected face: {saved_frame_path}')

        except Exception as e:
            logger.error(f'Error saving frame with detected face: {e}')

    async def send_error_notification(self, message):
        response_data = {'error': message}
        await self.send(text_data=json.dumps(response_data))

    async def send_processed_frame(self, frame_path):
        try:
            with open(frame_path, 'rb') as image_file:
                base64_frame = base64.b64encode(image_file.read()).decode('utf-8')

            await self.send(text_data=json.dumps({'processed_frame': base64_frame}))
            logger.info(f'Sent processed frame to the client: {frame_path}')
        except Exception as e:
            logger.error(f'Error sending processed frame: {e}')


















































