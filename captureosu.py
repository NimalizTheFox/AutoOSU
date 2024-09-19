import cv2
import mss
import win32gui
import win32api
import win32con
import numpy as np
import time
import pyautogui as pg


def get_frame(monitor):
    """
    Костыль, чтобы заставить GC видеть mss, иначе происходит утечка памяти
    :param monitor: область экрана, в которой нужно сделать скриншот
    :return: изображение как numpy массив
    """
    return np.asarray(mss.mss().grab(monitor))


def get_playfield_monitor(hwnd):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0] + 3
    y = rect[1] + 27
    w = rect[2] - x - 3
    h = rect[3] - y - 2

    monitor = {"top": y, "left": x, "width": w, "height": h}

    playfield = {
        'width': round(round(monitor['height'] * 0.8) * (4 / 3)),
        'height': round(monitor['height'] * 0.8)
    }

    playfield_monitor = {
        "top": y + round((monitor['height'] - playfield['height']) / 2 + round(playfield['height'] * 0.02)),
        "left": x + round((monitor['width'] - playfield['width']) / 2),
        "width": playfield['width'],
        "height": playfield['height']
    }
    return playfield_monitor


def screenshot_standardization(screenshot: np.ndarray, image_shape: tuple[int, int]) -> np.ndarray:
    """Перевод скриншота в ЧБ, изменение размера и стандартизация до [0..1] каждого пикселя"""
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)  # Переводим в ЧБ
    screenshot = cv2.resize(screenshot, dsize=(image_shape[0], image_shape[1]), interpolation=cv2.INTER_AREA)
    screenshot = screenshot.astype("float32") / 255
    return np.expand_dims(screenshot, -1)


def main():
    image_shape = (80, 60)

    # Возимся с разрешением и положением окна осу, делаем его главным окном
    hwnd = win32gui.FindWindow(None, "osu!")
    win32gui.ShowWindow(hwnd, 4)        # Вытаскивает окно из свернутого состояния, но не активирует
    win32gui.SetForegroundWindow(hwnd)  # Активирует приложение

    playfield_monitor = get_playfield_monitor(hwnd)

    MAX_FPS = 30
    MIN_FRAME_TIME = 1/MAX_FPS - 1/60

    new_time = time.time() - 10
    iterator = 0
    while True:
        start = time.time()

        if iterator % 50 == 0:
            old_lime = new_time
            new_time = time.time()
            # print(f"\rFPS: {1/((new_time - old_lime)/50)}", end='')
            iterator = 0

        screenshot = get_frame(playfield_monitor)
        # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)  # Переводим в ЧБ
        # screenshot = cv2.resize(screenshot, dsize=(image_shape[0], image_shape[1]), interpolation=cv2.INTER_AREA)
        # screenshot = cv2.resize(screenshot, dsize=(640, 480), interpolation=cv2.INTER_AREA)
        cv2.imshow('frame', screenshot)

        iterator += 1

        if cv2.waitKey(1) == ord('q'):
            # break
            # Работает, только если предварительно настроиться на окно Frame
            x, y = pg.position()
            y = (y - playfield_monitor['top'])/playfield_monitor['height']
            x = (x - playfield_monitor['left'])/playfield_monitor['width']
            print(x, y)

        time.sleep(max(0., MIN_FRAME_TIME - (time.time() - start)))


    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()