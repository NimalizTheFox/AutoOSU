import cv2
import mss
import win32gui
import win32api
import win32con
import numpy as np
import time
import pyautogui as pg

pg.PAUSE = 0
pg.FAILSAFE = False


def click(monitor, x, y):
    window_x = monitor['left']
    window_y = monitor['top']
    # pg.moveTo(window_x + x, window_y + y)
    pg.click(window_x + x, window_y + y)
    # pg.keyDown('x')     # Воспринимается, но в NOTE внутри сказано, что может он вероятно одноразовый, не зажимается


def get_frame(monitor):
    """
    Костыль, чтобы заставить GC видеть mss, иначе происходит утечка памяти
    :param monitor: область экрана, в которой нужно сделать скриншот
    :return: изображение как numpy массив
    """
    with mss.mss() as sct:
        sct_img = sct.grab(monitor)
        return np.asarray(sct_img)


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


def main():
    # Возимся с разрешением и положением окна осу, делаем его главным окном
    hwnd = win32gui.FindWindow(None, "osu!")
    win32gui.ShowWindow(hwnd, 4)        # Вытаскивает окно из свернутого состояния, но не активирует
    win32gui.SetForegroundWindow(hwnd)  # Активирует приложение

    playfield_monitor = get_playfield_monitor(hwnd)
    print(playfield_monitor)

    # screenshot = get_frame(monitor)

    # screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2GRAY)  # Переводим в ЧБ
    # screenshot = cv2.resize(screenshot, dsize=(image_shape[0], image_shape[1]), interpolation=cv2.INTER_AREA)
    # screenshot = screenshot.astype("float32") / 255
    # screenshot = np.expand_dims(screenshot, -1)

    fps_buffer = [0. for _ in range(120)]
    old_lime = time.time()
    iterator = 0
    screenshot = get_frame(playfield_monitor)

    MAX_FPS = 30
    MIN_FRAME_TIME = 1/MAX_FPS - 1/60

    new_time = time.time() - 10

    # while True:
    #     start = time.time()
    #
    #     if iterator % 50 == 0:
    #         old_lime = new_time
    #         new_time = time.time()
    #         print(f"\rFPS: {1/((new_time - old_lime)/50)}", end='')
    #
    #     # screenshot = get_frame(monitor)
    #     screenshot = get_frame(playfield_monitor)
    #     cv2.imshow('frame', screenshot)
    #
    #     iterator += 1
    #
    #     if cv2.waitKey(1) == ord('q'):
    #         break
    #
    #     time.sleep(max(0., MIN_FRAME_TIME - (time.time() - start)))
    #
    #
    # cv2.destroyAllWindows()


if __name__ == '__main__':
    main()