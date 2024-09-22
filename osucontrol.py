import pyautogui as pg
import asyncio
import time
import os

pg.PAUSE = 0
pg.FAILSAFE = False


class MenuController:
    def __init__(self, playfield_monitor, osu_folder):
        self.playfield_monitor = playfield_monitor
        self.osu_folder = osu_folder

    def _mouse_click(self, cords):
        x = round(self.playfield_monitor['left'] + cords[0] * self.playfield_monitor['width'])
        y = round(self.playfield_monitor['top'] + cords[1] * self.playfield_monitor['height'])
        pg.moveTo(x, y)
        pg.click()
        time.sleep(0.5)

    def _press_key(self, key_name):
        pg.keyDown(key_name)
        pg.sleep(0.1)
        pg.keyUp(key_name)

    def get_songs(self):
        dirs = os.listdir(self.osu_folder + r'/Songs')
        names = [" ".join(folder.split(' ')[1:]) for folder in dirs]
        # TODO: Доделать


    def from_start_to_song_list(self):
        self._mouse_click((0.5, 0.5))
        self._mouse_click((0.7, 0.22))
        self._mouse_click((0.7, 0.30))
        self._mouse_click((0.47, 0.38))

    def to_top_song_list(self):
        self._press_key('down')
        pg.sleep(0.5)
        for _ in range(100):    # Нужно высчитать сколько песен в папке osu и от этого делать скролы (кол-во папок + 10)
            pg.scroll(1)
            pg.sleep(0.005)
        self._mouse_click((0.88, 0.55))


class PlayFieldController:
    def __init__(self, playfield_monitor):
        self.playfield_monitor = playfield_monitor
        self.actions_queue = asyncio.Queue()
        asyncio.create_task(self.click_and_move())

    async def click_and_move(self):
        # По-хорошему нужно зарандомить кнопку, но пока без этого
        print("работаем!")
        while True:
            action = await self.actions_queue.get()

            x = round(self.playfield_monitor['left'] + action[0][0] * self.playfield_monitor['width'])
            y = round(self.playfield_monitor['top'] + action[0][1] * self.playfield_monitor['height'])
            if action[1] == 0:
                pg.keyUp('x')
                pg.moveTo(x, y)
            elif action[1] == 1:
                pg.keyUp('x')   # На случай, если идет сразу после д2
                pg.moveTo(x, y)
                pg.keyDown('z')
                # pg.sleep(0.01)
                await asyncio.sleep(0.01)
                pg.keyUp('z')
            else:
                pg.moveTo(x, y)
                pg.keyDown('x')

            self.actions_queue.task_done()

