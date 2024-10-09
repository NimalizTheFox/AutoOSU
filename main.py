import os
import asyncio
import numpy as np
import time

import osufiles
from osuneuro import load_model, compute_action
from captureosu import get_frame, get_playfield_monitor, screenshot_standardization, get_hwnd, get_window_text
from osucontrol import PlayFieldController
from osuparser import get_osu_process
from replayRepeater import get_timer_address, read_from_memory


async def main():
    osu_folder = osufiles.OSU_PATH
    image_shape = (80, 60)
    images_in_set = 4

    offsets = (0x8, 0x8, 0x3F4, 0xA4)   # Для версии b20241001

    max_fps = 30
    min_frame_time = 1 / max_fps - 1 / 60

    if not os.path.exists('model.keras'):
        print('Сначала обучите модель!\nДостаточно просто запустить osu!, перейти в список песен и запустить файл datacollection.py, все остальное сделает автоматика\n')
        raise FileExistsError('Модель отсутствует!')

    osu_process = get_osu_process(osu_folder)
    timer_address = get_timer_address(osu_process, offsets) + offsets[-1]

    model = load_model()
    print('Модель загружена')

    hwnd = get_hwnd()
    print(f'Процесс osu! найден: {hwnd}')

    playfield_monitor = get_playfield_monitor(hwnd)

    # Контроллер
    controller = PlayFieldController(playfield_monitor)

    # menu.start_current_song()
    while True:
        print('Ожидание начала песни')
        np_screenshots = np.zeros((1, images_in_set, image_shape[1], image_shape[0], 1), np.float16)

        # Ожидаем пока не начнется песня
        while get_window_text(hwnd) == "osu!":
            time.sleep(0.01)

        timer = read_from_memory(osu_process, timer_address)
        iterator = 0

        # Начало песни
        while get_window_text(hwnd) != "osu!":  # Пока не появятся результаты
            start = time.time()

            old_timer = timer
            timer = read_from_memory(osu_process, timer_address)

            if timer == old_timer:
                iterator += 1
            else:
                iterator = 0

            while iterator > 2 and old_timer == timer:
                old_timer = timer
                timer = read_from_memory(osu_process, timer_address)

            screenshot = get_frame(playfield_monitor)
            screenshot = screenshot_standardization(screenshot, image_shape)

            np_screenshots = np.roll(np_screenshots, -1, axis=1)
            np_screenshots[0][-1] = screenshot

            action = compute_action(model, np_screenshots)
            controller.actions_queue.put_nowait(action)

            await asyncio.sleep(max(0., min_frame_time - (time.time() - start)))  # Обеспечение нужного фреймрейта






if __name__ == '__main__':
    asyncio.run(main())
