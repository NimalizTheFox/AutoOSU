import time
import numpy as np
from captureosu import get_frame, get_playfield_monitor
import win32gui

from osuneuro import create_model, compute_action
from captureosu import screenshot_standardization, get_hwnd


image_shape = (80, 60)
images_in_set = 4
input_image_shape = (images_in_set, image_shape[1], image_shape[0], 1)

hwnd = get_hwnd()
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

    ress.append(result)
    times.append(round(time.time() - start, 4))



print(time.time() - start_time)

print(times)
print(ress)