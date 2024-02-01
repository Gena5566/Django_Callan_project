import os
import django
from django.conf import settings
import face_recognition

# Установите переменную окружения DJANGO_SETTINGS_MODULE для указания настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DjangoCallanProject.settings")

django.setup()

from usersapp.models import BlogUser, Profile
from PIL import Image

# Создайте словарь для хранения информации о пользователях и их изображениях
user_images_dict = {}

# Получите список всех пользователей
all_users = BlogUser.objects.all()

# Пройдитесь по каждому пользователю
for user in all_users:
    # Получите имя пользователя
    username = user.username

    # Получите URL изображения лица
    face_image_url = user.face_image.url if user.face_image else None

    # Получите информацию из профиля, если она есть
    profile = Profile.objects.get(user=user)
    profile_info = profile.info if profile else None

    # Выведите информацию о пользователе
    #print(f"Username: {username}, Face Image URL: {face_image_url}, Profile Info: {profile_info}")

    # Получите путь к файлу изображения
    image_path = os.path.join(settings.MEDIA_ROOT, str(user.face_image))

    # Проверьте совпадение URL изображения с именем файла
    if os.path.exists(image_path):
        user_images_dict[username] = image_path
    else:
        print(f"Image not found for user {username}")

# Выведите словарь с именами пользователей и соответствующими файлами изображений
#print("User Images Dictionary:")
#print(user_images_dict)

# Создайте словарь для хранения векторных эмбеддингов лиц
embedding_faces = {}

# Пройдитесь по словарю
for username, image_path in user_images_dict.items():
    #print(f"Processing image for user {username}")

    # Загрузите изображение с помощью библиотеки PIL
    image = face_recognition.load_image_file(image_path)

    # Обнаружение лиц на изображении
    face_locations = face_recognition.face_locations(image)

    # Получение векторных эмбеддингов для обнаруженных лиц
    face_encodings = face_recognition.face_encodings(image, face_locations)

    # Вывод векторных эмбеддингов
    for face_encoding in face_encodings:
        #print(face_encoding)
        # Сохраните векторные эмбеддинги в словаре
        if username not in embedding_faces:
            embedding_faces[username] = []
        embedding_faces[username].append(face_encoding)

    #if not face_locations:
        #print(f"No face detected for user {username}")
    #else:
        #print(f"Face detected for user {username}")

# Выведите словарь с векторными эмбеддингами
#print("Face Embeddings Dictionary:")
#print(embedding_faces)

# Построение абсолютного пути к изображению "Фото.jpg" внутри папки проекта
image_path_test = os.path.join(settings.BASE_DIR, 'foto.jpg')

# Загрузите изображение с помощью библиотеки PIL
image = face_recognition.load_image_file(image_path_test)

# Обнаружение лиц на изображении
face_locations = face_recognition.face_locations(image)

# Получение векторных эмбеддингов для обнаруженных лиц
face_encodings = face_recognition.face_encodings(image, face_locations)
# Вывод векторных эмбеддингов
for face_encoding in face_encodings:
    print(face_encoding)


from scipy.spatial import distance

# Векторные эмбеддинги для изображения "Фото.jpg"
test_face_encoding = face_encodings[0]  # Предполагаем, что на изображении одно лицо

# Проход по словарю векторных эмбеддингов
for username, user_embeddings in embedding_faces.items():
    # Проход по всем векторам пользователя
    for user_embedding in user_embeddings:
        # Рассчитываем косинусное расстояние между векторами
        dist = distance.cosine(test_face_encoding, user_embedding)

        # Если расстояние ниже определенного порога, считаем, что это тот же пользователь
        if dist < 0.9:  # Примерный порог, может потребоваться настройка
            print(f"Изображение 'Фото.jpg' принадлежит пользователю {username}")
            break


from deepface import DeepFace
import cv2
import matplotlib.pyplot as plt
import os
from django.conf import settings

# Построение абсолютного пути к изображению "Фото.jpg" внутри папки проекта
img1_path = os.path.join(settings.MEDIA_ROOT, 'user_faces/IMG_8304.JPG')
# Получите путь к файлу изображения
img2_path = os.path.join(settings.BASE_DIR, 'foto.jpg')

def verify(img1_path, img2_path):
    # Загрузка изображения 1
    img1 = cv2.imread(img1_path)
    if img1 is None:
        print(f"Ошибка загрузки изображения: {img1_path}")
        return

    # Загрузка изображения 2
    img2 = cv2.imread(img2_path)
    if img2 is None:
        print(f"Ошибка загрузки изображения: {img2_path}")
        return

    # Отображение изображений
    #plt.imshow(img1[:,:,::-1])
    #plt.show()
    #plt.imshow(img2[:,:,::-1])
    #plt.show()

    # Проверка с использованием DeepFace
    output = DeepFace.verify(img1_path, img2_path)
    print(output)
    verification = output['verified']
    if verification:
       print('Они одинаковы')
    else:
       print('Они не одинаковы')

verify(img1_path, img2_path)










