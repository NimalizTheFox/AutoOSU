import pyautogui as pg
import asyncio
import time
import os

from captureosu import get_playfield_monitor, get_hwnd
from osufiles import get_song_list


pg.PAUSE = 0
pg.FAILSAFE = False


class MenuController:
    def __init__(self, playfield_monitor, song_folders_number):
        self.playfield_monitor = playfield_monitor
        self.scroll_len = song_folders_number

    def _mouse_click(self, cords):
        x = round(self.playfield_monitor['left'] + cords[0] * self.playfield_monitor['width'])
        y = round(self.playfield_monitor['top'] + cords[1] * self.playfield_monitor['height'])
        pg.moveTo(x, y)
        pg.click()
        pg.sleep(0.5)

    def _press_key(self, key_name):
        pg.keyDown(key_name)
        pg.sleep(0.1)
        pg.keyUp(key_name)

    def from_start_to_song_list(self):
        self._mouse_click((0.5, 0.5))
        self._mouse_click((0.7, 0.22))
        self._mouse_click((0.7, 0.30))
        self._mouse_click((0.47, 0.38))

    def to_top_song_list(self):
        self._press_key('down')
        pg.sleep(0.5)
        for _ in range(self.scroll_len + 10):
            pg.scroll(1)
            pg.sleep(0.005)
        self._mouse_click((0.88, 0.55))

    def autoplay_mod_on(self):
        self._mouse_click((0.26, 0.98))
        self._mouse_click((0.73, 0.59))
        self._press_key('esc')

    def choose_certain_song(self, cords):
        """Тут должен быть выбор конкретной песни, передается координатами (сколько нажать вниз и вправо)
        Вниз переключает автора, вправо - выбор конкретной песни"""
        # Выбор конкретной песни из всех
        self.to_top_song_list()
        for _ in range(cords[0]):
            self._press_key('down')
            pg.sleep(0.05)
        for _ in range(cords[1]):
            self._press_key('right')
            pg.sleep(0.05)

    def save_replay(self):
        self._press_key('f2')

    def start_current_song(self):
        pg.sleep(0.1)
        self._mouse_click((0.55, 0.43))
        pg.sleep(0.05)
        self._mouse_click((0.55, 0.43))

    def speedup_replay(self):
        pg.sleep(0.06)
        self._mouse_click((1.02, 0.27))

    def escape_from_results(self):
        pg.sleep(0.1)
        self._press_key('esc')
        pg.sleep(0.4)

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


def main():
    OSU_PATH = r"D:\Games\osu!"
    if not os.path.exists(OSU_PATH):
        OSU_PATH = r"C:\Games\osu!"

    hwnd = get_hwnd()
    playfield_monitor = get_playfield_monitor(hwnd)

    # тесты контроллера поля в tests2.py, так как там нужна асинхронная функция

    menu = MenuController(playfield_monitor, len(get_song_list(OSU_PATH)))
    # menu.from_start_to_song_list()
    # menu.to_top_song_list()
    menu.autoplay_mod_on()

    menu.choose_certain_song((3, 0))
    menu.start_current_song()
    menu.speedup_replay()



if __name__ == '__main__':
    main()
