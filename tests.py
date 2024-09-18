import struct
import time
import cv2
import numpy as np
from captureosu import get_frame, get_playfield_monitor
import win32gui


def screenshot_standardization(screenshot: np.ndarray, image_shape: tuple[int, int]) -> np.ndarray:
    """Перевод скриншота в ЧБ, изменение размера и стандартизация до [0..1] каждого пикселя"""
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)  # Переводим в ЧБ
    screenshot = cv2.resize(screenshot, dsize=(image_shape[0], image_shape[1]), interpolation=cv2.INTER_AREA)
    screenshot = screenshot.astype("float32") / 255
    return np.expand_dims(screenshot, -1)


image_shape = (80, 60)


hwnd = win32gui.FindWindow(None, "osu!")
win32gui.ShowWindow(hwnd, 4)        # Вытаскивает окно из свернутого состояния, но не активирует
win32gui.SetForegroundWindow(hwnd)  # Активирует приложение

time.sleep(0.5)

playfield_monitor = get_playfield_monitor(hwnd)

start_time = time.time()
for i in range(1):
    screenshot = get_frame(playfield_monitor)
    # все операции по изменению скрина занимают ~3-5мс в среднем
    screenshot = screenshot_standardization(screenshot, image_shape)    # ~3-5 мс
    # print(type(screenshot))
    print(screenshot.shape)
print(time.time() - start_time)
