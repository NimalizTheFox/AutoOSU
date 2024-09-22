import time

import mss
import cv2
import pyautogui as pg  # Он шустрый если сделать pg.PAUSE = 0
import prprcedog  # файл питона, возможность залезть в области данных ОЗУ из CheatEngine
import os
import asyncio

OSU_PATH = r"D:\Games\osu!"
if not os.path.exists(OSU_PATH):
    OSU_PATH = r"C:\Games\osu!"


async def main():
    image_shape = (80, 60)
    images_in_set = 4
    input_image_shape = (images_in_set, image_shape[1], image_shape[0], 1)




if __name__ == '__main__':
    main()