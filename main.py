import time

import mss
import cv2
import pyautogui as pg  # Он шустрый если сделать pg.PAUSE = 0
import prprcedog  # файл питона, возможность залезть в области данных ОЗУ из CheatEngine
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

pg.PAUSE = 0
pg.FAILSAFE = False
OSU_PATH = r"D:\Games\osu!\osu!.exe"

# Смещения в памяти для соответствующих параметров
offsets_timer = [0x20, 0x32C, 0xBC4]
offsets_score = [0x8, 0xB8, 0xC, 0x42C, 0xA0, 0x78]  # Смещения указателей для счета
offsets_combo = [0x8, 0xB8, 0xC, 0x42C, 0xA0, 0x94]  # Смещения указателей для комбо
offsets = [offsets_score, offsets_combo, offsets_timer]


def main():
    pass


if __name__ == '__main__':
    main()