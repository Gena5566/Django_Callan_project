document.addEventListener("DOMContentLoaded", function () {

    const startCameraButton = document.getElementById("startCameraButton");
    const takePhotoButton = document.getElementById("takePhotoButton");
    const downloadPhotoButton = document.getElementById("downloadPhotoButton"); // Добавил поиск кнопки "Сохранить фото"
    const outputImageElement = document.getElementById("outputImage");

    // Инициализация переменных
    let mediaStream;
    let currentPhotoData;

    function startCamera() {
        console.log("Запуск камеры...");

        // Получить доступ к камере
        navigator.mediaDevices.getUserMedia({
            video: true,
        })
            .then(function (stream) {
                // Установить ширину видеопотока
                videoElement.width = 400;

                console.log("Камера включена успешно.");
                mediaStream = stream;
                videoElement.srcObject = stream;
                videoElement.style.display = "block";
            })
            .catch(function (error) {
                console.error("Ошибка при включении камеры:", error);
            });
    }

    function takePhoto() {
        if (mediaStream) {
            console.log("Создание снимка...");

            // Создать холст для рисования изображения
            const canvas = document.createElement('canvas');
            canvas.width = videoElement.videoWidth;
            canvas.height = videoElement.videoHeight;

            // Получить контекст холста
            const context = canvas.getContext('2d');

            // Нарисовать изображение с камеры на холсте
            context.drawImage(videoElement, 0, 0, canvas.width, canvas.height);

            console.log("Фото успешно создано на клиенте.");

            // Сохраняем данные снимка в формате base64
            currentPhotoData = canvas.toDataURL('image/png');

            // Преобразуем данные снимка в объект Blob
            currentPhotoData = dataURItoBlob(currentPhotoData);

            // Добавим логи для отладки
            console.log("Тип данных (currentPhotoData):", currentPhotoData.type);
            console.log("Размер данных (currentPhotoData):", currentPhotoData.size);

            // Проверим, что outputImageElement существует и является изображением
            if (outputImageElement && outputImageElement.tagName.toLowerCase() === 'img') {
                // Установить изображение на элемент outputImageElement
                outputImageElement.src = URL.createObjectURL(currentPhotoData);
                outputImageElement.style.display = "block";

                // Отключаем камеру
                mediaStream.getTracks().forEach(track => track.stop());
                console.log("Камера успешно выключена.");
                // Скрываем видео
                videoElement.style.display = "none";
            } else {
                console.error("Элемент с id 'outputImage' не найден или не является изображением (img).");
            }
        } else {
            console.error("Камера не включена.");
        }
    }

    function downloadPhoto() {
        if (currentPhotoData) {
            console.log("Загрузка фото...");

            console.log("Тип данных (currentPhotoData):", typeof currentPhotoData);
            console.log("Содержимое (currentPhotoData):", currentPhotoData);

            // Преобразование данных изображения в объект Blob
            const blob = currentPhotoData;
            console.log(blob);

            // Создание ссылки для скачивания файла
            const url = window.URL.createObjectURL(blob);
            console.log(url);

            // Создание элемента <a> для скачивания файла
            const a = document.createElement('a');
            a.href = url;
            a.download = 'face.png';

            console.log('Попытка создать элемент для скачивания файла...');

            // Имитация клика для скачивания файла
            a.click();

            console.log('Имитация клика для скачивания файла...');

            // Удаление элемента и освобождение ресурсов
            window.URL.revokeObjectURL(url);
        } else {
            console.error("Отсутствуют данные фото для загрузки.");
        }
    }

    if (startCameraButton) {
        startCameraButton.addEventListener("click", startCamera);
    } else {
        console.error("Элемент с id 'startCameraButton' не найден.");
    }

    if (takePhotoButton) {
        takePhotoButton.addEventListener("click", takePhoto);
    } else {
        console.error("Элемент с id 'takePhotoButton' не найден.");
    }

    if (downloadPhotoButton) { // Добавил проверку наличия кнопки "Сохранить фото"
        downloadPhotoButton.addEventListener("click", downloadPhoto);
    } else {
        console.error("Элемент с id 'downloadPhotoButton' не найден.");
    }

    // Функция для преобразования Data URI в Blob
    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(",")[1]);
        const ia = new Uint8Array(byteString.length);
        for (let i = 0; i < byteString.length; i++) {
            ia[i] = byteString.charCodeAt(i);
        }
        return new Blob([ia], { type: "image/png" });
    }
});





















