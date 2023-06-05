# pip3 install -r requirements.txt
# sudo python3 make_dataset.py

import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import os
import keyboard
import time
from colorama import Fore, Style, Back
from tqdm import tqdm
import re


# папка, куда будут сохраняться аудиофайлы
output_folder = "wavs/"

# создаем папку, если она еще не создана
os.makedirs(output_folder, exist_ok=True)

# список предложений для озвучивания
with open('sentences.txt', 'r') as file:
    sentences = [line.strip() for line in file]

# частота дискретизации
fs = 22050  # Sample rate

buffer = []

# Callback функция для потока записи.
def callback(indata, frames, time, status):
    buffer.append(indata.copy())

# Последний ID аудио файла
last_id = max([int(re.findall(r'\d+', file)[0]) for file in os.listdir(output_folder)], default=-1)

print(Fore.YELLOW + "Начинаем процесс записи..." + Style.RESET_ALL)

for i, sentence in tqdm(enumerate(sentences, start=last_id + 1), total=len(sentences), desc=Fore.CYAN + "Прогресс записи" + Style.RESET_ALL):
    while True:  # позволяем пользователю повторять запись текущего предложения
        print()  # пустая строка для разделения каждого нового предложения

        print(Fore.YELLOW + f"Озвучьте следующее предложение: " + Back.RED + f"{sentence}" + Style.RESET_ALL)
        print(Fore.YELLOW + "Нажмите пробел для начала записи..." + Style.RESET_ALL)

        while True:  # ждем нажатия пробела
            if keyboard.is_pressed('space'):
                break
            else:
                time.sleep(0.1)

        print(Fore.GREEN + "Начинаю запись. Нажмите пробел для окончания записи..." + Style.RESET_ALL)

        buffer.clear()
        with sd.InputStream(callback=callback, channels=1, samplerate=fs) as stream:
            while True:  # запись аудио
                if keyboard.is_pressed('space'):
                    break
                else:
                    time.sleep(0.1)

        print(Fore.GREEN + "Нажмите пробел ещё раз, чтобы сохранить запись. Нажмите любую другую клавишу, чтобы удалить запись и попробовать снова." + Style.RESET_ALL)

        while True:  # ждем нажатия пробела или любой другой клавиши
            if keyboard.is_pressed('space'):
                if buffer:  # только если буфер не пуст
                    filename = f"{output_folder}/{i}-audio.wav"
                    recording = np.concatenate(buffer, axis=0)
                    write(filename, fs, recording)
                    print(Fore.GREEN + "Запись сохранена." + Style.RESET_ALL)

                    # Запись в файл субтитров
                    with open('subtitles.txt', 'a') as subs:
                        subs.write(f"{filename}|{sentence}\n")
                break
            elif keyboard.read_key() != 'space':
                print(Fore.RED + "Запись удалена. Попробуйте записать снова." + Style.RESET_ALL)
                break
        if keyboard.is_pressed('space'):
            break

print(Fore.GREEN + "Все предложения записаны. Запись закончена!" + Style.RESET_ALL)
