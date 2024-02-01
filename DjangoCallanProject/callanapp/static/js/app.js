let mediaRecorder;
let localVideo = document.getElementById('localVideo');
let startButton = document.getElementById('startButton');
let sentButton = document.getElementById('sentButton');
let ws;
let stopRecordingTimeout;

// Подключение к WebSocket
function connectWebSocket() {
    return new Promise(resolve => {
        ws = new WebSocket('ws://' + window.location.host + '/ws/video_stream_group/');

        ws.onopen = function (event) {
            console.log('WebSocket соединение установлено.');
            resolve();
        };

        ws.onmessage = function (event) {
            var data = JSON.parse(event.data);
            console.log('Получено сообщение от сервера:', data);

            if (data.processed_frame) {
                console.log('Декодирование и отображение изображения...');
                decodeAndDisplayImage(data.processed_frame);
            }
        };

        ws.onclose = function (event) {
            console.log('WebSocket соединение закрыто.');
        };
    });
}

// Код для отправки видео на сервер
function sendVideoFrame(frame) {
    try {
        if (frame && frame.size > 0) {
            const format = 'video/x-matroska';
            const size = frame.size || 'unknown';

            const arrayBuffer = new ArrayBuffer(frame.size);
            const uint8Array = new Uint8Array(arrayBuffer);

            const reader = new FileReader();
            reader.onloadend = function () {
                uint8Array.set(new Uint8Array(reader.result));
                ws.send(arrayBuffer);
                console.log('Отправлены видеоданные на сервер. Формат:', format, 'Размер:', size);
            };
            reader.readAsArrayBuffer(frame);
        } else {
            throw new Error('Кадр пуст. Невозможно отправить пустой кадр на сервер.');
        }
    } catch (error) {
        console.error('Ошибка отправки видеоданных на сервер:', error.message);
    }
}

function decodeAndDisplayImage(base64Data) {
    try {
        const faceImageField = document.getElementById('id_face_image');
        if (faceImageField && faceImageField.type === 'file') {
            const blob = base64ToBlob(base64Data);

            // Создаем объект File из Blob
            const file = new File([blob], 'fase_client.png', { type: 'image/png' });

            // Создаем объект FileList и устанавливаем его в поле файла
            const fileList = new FileList([file]);
            faceImageField.files = fileList;

            console.log('Изображение успешно декодировано и установлено в поле формы.');
        } else {
            console.error('Поле формы face_image не найдено или не является полем типа "file".');
        }
    } catch (error) {
        console.error('Ошибка при декодировании и установке изображения в поле формы:', error);
    }
}


// Функция для преобразования base64 в Blob
function base64ToBlob(base64Data) {
    const byteString = atob(base64Data);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const intArray = new Uint8Array(arrayBuffer);

    for (let i = 0; i < byteString.length; i++) {
        intArray[i] = byteString.charCodeAt(i);
    }

    return new Blob([intArray], { type: 'image/png' });
}

// Получение доступа к видеокамере и начало записи видео
async function startRecording() {
    try {
        await connectWebSocket();
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        console.log('Доступ к камере разрешен.');

        localVideo.srcObject = stream;

        // Очистка таймера перед началом новой записи
        clearTimeout(stopRecordingTimeout);

        stopRecordingTimeout = setTimeout(() => {
            mediaRecorder.stop();
        }, 3000);

        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            if (event.data.size > 0) {
                const videoFrame = event.data;
                sendVideoFrame(videoFrame);
            }
        };

        mediaRecorder.onstop = () => {
            localVideo.srcObject.getTracks().forEach(track => track.stop());
            console.log('Запись остановлена.');
            startButton.disabled = false;
            sentButton.disabled = false;
        };

        mediaRecorder.start();
        startButton.disabled = true;
        sentButton.disabled = true;

        const tracks = stream.getVideoTracks();
        if (tracks.length > 0) {
            console.log('Тип видеопотока:', tracks[0].kind);
            console.log('Размеры видеопотока:', tracks[0].getSettings().width, 'x', tracks[0].getSettings().height);
        }
    } catch (error) {
        console.error('Ошибка доступа к медиа-устройствам: ', error);
    }
}

function sentRecording() {
    console.log('Video sent to the server.');
}

startButton.addEventListener('click', startRecording);
sentButton.addEventListener('click', sentRecording);












