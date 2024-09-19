import struct
import time
import cv2
import numpy as np
from captureosu import get_frame, get_playfield_monitor
import win32gui

from osuneuro import create_model, compute_action


def screenshot_standardization(screenshot: np.ndarray, image_shape: tuple[int, int]) -> np.ndarray:
    """Перевод скриншота в ЧБ, изменение размера и стандартизация до [0..1] каждого пикселя"""
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)  # Переводим в ЧБ
    screenshot = cv2.resize(screenshot, dsize=(image_shape[0], image_shape[1]), interpolation=cv2.INTER_AREA)
    screenshot = screenshot.astype("float32") / 255
    return np.expand_dims(screenshot, -1)


image_shape = (80, 60)
images_in_set = 4
input_image_shape = (images_in_set, image_shape[1], image_shape[0], 1)

hwnd = win32gui.FindWindow(None, "osu!")
win32gui.ShowWindow(hwnd, 4)        # Вытаскивает окно из свернутого состояния, но не активирует
win32gui.SetForegroundWindow(hwnd)  # Активирует приложение

time.sleep(0.5)

playfield_monitor = get_playfield_monitor(hwnd)

print('Создание модели...')
model = create_model(input_image_shape)
print('Модель создана')
times = []
ress = []

start_time = time.time()

# Чёрная заглушка для первого набора скриншотов
np_screenshots = np.zeros(shape=(1, images_in_set, image_shape[1], image_shape[0], 1))

for i in range(10):
    start = time.time()
    screenshot = get_frame(playfield_monitor)

    # все операции по изменению скрина занимают ~3-5мс в среднем
    screenshot = screenshot_standardization(screenshot, image_shape)    # ~3-5 мс
    # print(type(screenshot))

    np_screenshots = np.roll(np_screenshots, -1, axis=1)
    np_screenshots[0][-1] = screenshot
    # result = model(np_screenshots)
    result = compute_action(model, np_screenshots)

    # [1.8993, 0.1313, 0.0905, 0.084, 0.083]

    times.append(round(time.time() - start, 4))
    ress.append(result)


print(time.time() - start_time)

print(times)
print(ress)