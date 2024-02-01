document.addEventListener("DOMContentLoaded", function () {
    const nameInput = document.getElementById("name-input");
    const sendNameButton = document.getElementById("sendNameButton");
    const startCameraButton = document.getElementById("startCameraButton");
    const takePhotoButton = document.getElementById("takePhotoButton");
    const sendPhotoButton = document.getElementById("sendPhotoButton");
    const videoElement = document.getElementById("videoElement");
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

            // Установить изображение на элемент outputImageElement
            outputImageElement.src = URL.createObjectURL(currentPhotoData);
            outputImageElement.style.display = "block";

            // Отключаем камеру
            mediaStream.getTracks().forEach(track => track.stop());
            console.log("Камера успешно выключена.");
            // Скрываем видео
            videoElement.style.display = "none";
        } else {
            console.error("Камера не включена.");
        }
    }

    // Функция для отправки имени пользователя на сервер
    function sendName() {
        if (!nameInput) {
            console.error("Элемент с id 'name-input' не найден.");
            return;
        }

        const name = nameInput.value;
        const csrfToken = document.getElementsByName("csrfmiddlewaretoken")[0].value;

        $.ajax({
            url: "/users/receive_username/",
            type: "POST",
            data: {
                'username': name,
                'csrfmiddlewaretoken': csrfToken,
            },
            success: function (data) {
                if (data.success) {
                    console.log("Имя успешно отправлено");
                    document.getElementById("success-message").innerText = "Имя успешно отправлено!";
                } else {
                    console.log("Ошибка при отправке имени");
                }
            },
            error: function (error) {
                console.error("Произошла ошибка при выполнении AJAX-запроса:", error);
            }
        });
    }


    // Функция для отправки фото на сервер
    function sendPhoto() {
        const formData = new FormData();

        if (currentPhotoData !== undefined) {
            console.log("Данные изображения определены");
            console.log("Тип данных (currentPhotoData):", currentPhotoData.type);
            console.log("Размер данных (currentPhotoData):", currentPhotoData.size);

            const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;

            formData.append("photo_data", currentPhotoData);
            console.log("Данные сформированы перед отправкой");
            console.log("Тип данных (formData):", formData.get("photo_data").type);
            console.log("Размер данных (formData):", formData.get("photo_data").size);

            fetch("/users/receive_face/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrfToken,
                },
                body: formData,
            })
            .then(response => handleResponse(response))
            .then(data => {
                if (data.status === "success" || data.success) {
                    console.log("Данные успешно отправлены на сервер.");
                } else {
                    console.error("Произошла ошибка при обработке данных на сервере.");
                }
            })
            .catch((error) => {
                console.error("Произошла ошибка при выполнении AJAX-запроса:", error);
                console.log("Текст ошибки:", error.message);
            });
        }
    }

    // Общая функция для обработки разных типов ответов
    function handleResponse(response) {
        const contentType = response.headers.get('content-type');
        console.log("Content-Type:", contentType);

        if (contentType && contentType.includes('application/json')) {
            return response.json();
        } else {
            return response.text().then(data => {
                console.log("Содержимое ответа:", data);
                return { success: true, html: data }; // Помечаем успешный ответ с HTML-контентом
            });
        }
    }

    function dataURItoBlob(dataURI) {
        const byteString = atob(dataURI.split(",")[1]);
        const ia = new Uint8Array(Uint8Array.from(byteString, c => c.charCodeAt(0)));
        return new Blob([ia], { type: "image/png" });
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

    if (sendNameButton) {
        sendNameButton.addEventListener("click", sendName);
    } else {
        console.error("Элемент с id 'sendNameButton' не найден.");
    }

    if (sendPhotoButton) {
        sendPhotoButton.addEventListener("click", sendPhoto);
    } else {
        console.error("Элемент с id 'sendPhotoButton' не найден.");
    }
});














