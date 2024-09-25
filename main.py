import os
import asyncio

import captureosu
import osufiles

OSU_PATH = r"D:\Games\osu!"
if not os.path.exists(OSU_PATH):
    OSU_PATH = r"C:\Games\osu!"


async def main():
    image_shape = (80, 60)
    images_in_set = 4
    input_image_shape = (images_in_set, image_shape[1], image_shape[0], 1)

    hwnd = captureosu.get_hwnd()
    playfield_monitor = captureosu.get_playfield_monitor(hwnd)




if __name__ == '__main__':
    asyncio.run(main())