import time
import windows
import prprcedog
import win32gui
import os
import pyautogui as pg

from captureosu import get_playfield_monitor
from osuparser import get_actions_list_from_replay

pg.PAUSE = 0
pg.FAILSAFE = False

OSU_PATH = r"D:\Games\osu!\osu!.exe"


def get_timer_address(osu_process, offsets):
    """Проходит по смещениям и возвращает адрес таймера"""
    pointerList = prprcedog.ThreadStackFinder.get_ce_thread_stack("osu!.exe")
    address_timer = int.from_bytes(osu_process.read_memory(int(pointerList[0], 16) - 0x00000988, 4), 'little')
    for offset in offsets[:-1]:
        address_timer = int.from_bytes(osu_process.read_memory(address_timer + offset, 4), "little")
    return address_timer


def read_from_memory(process, memory_address):
    return int.from_bytes(process.read_memory(memory_address, 4), "little", signed=True)


def click_and_move(playfield_monitor, action):
    x = round(playfield_monitor['left'] + action[1] * playfield_monitor['width'])
    y = round(playfield_monitor['top'] + action[2] * playfield_monitor['height'])
    if action[3] == 0:
        pg.keyUp('x')
        pg.moveTo(x, y)
    elif action[3] == 1:
        pg.keyUp('x')   # На случай, если идет сразу после д2
        pg.moveTo(x, y)
        pg.keyDown('z')
        pg.sleep(0.01)
        pg.keyUp('z')
    else:
        pg.moveTo(x, y)
        pg.keyDown('x')


def main():
    """Чит для osu! на идеальное прохождение карт. Тут отрабатывается скорость взаимодействия управления с игрой."""
    process_name = "osu!.exe"
    path_rep = 'osu_repls/osu! - Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal] (2024-09-07) Osu.osr'

    osu_process = None

    offsets = (0x128, 0x58, 0x32C, 0xC64)   # Для версии b20240820.1

    # Запуск и выделение процесса osu
    while osu_process is None:
        process_list = windows.system.enumerate_processes()
        for process in process_list:
            if process.name == process_name:
                osu_process = process
                break
        if osu_process is None:
            os.startfile(OSU_PATH)

    hwnd = win32gui.FindWindow(None, "osu!")
    # win32gui.ShowWindow(hwnd, 4)        # Вытаскивает окно из свернутого состояния, но не активирует
    win32gui.ShowWindow(hwnd, 5)        # Вытаскивает окно из свернутого состояния и активирует
    win32gui.SetForegroundWindow(hwnd)  # Активирует приложение
    time.sleep(1)

    playfield_monitor = get_playfield_monitor(hwnd)
    actions_list = get_actions_list_from_replay(path_rep)

    timer_address = get_timer_address(osu_process, offsets) + offsets[-1]

    print('Начало работы')

    while True:
        timer = read_from_memory(osu_process, timer_address)
        if timer == 0:
            while timer == 0:
                timer = read_from_memory(osu_process, timer_address)
            print('Началась новая песня!')

            time_timer = 0
            start_time = time.time() - 0.015

            while timer <= 15:
                timer = read_from_memory(osu_process, timer_address)
                time_timer = round((time.time() - start_time) * 1000)

            start_time += (time_timer - timer - 1)/1000     # Система смещения, чтобы таймеры соответствовали друг-другу

            # ====== НАЧАЛО ПЕСНИ ======
            iterator = 0
            action_iterator = 0
            while iterator < 5000:  # Пока таймер идет (смена занимает ~2000 чистых итераций)
                old_timer = timer
                time_timer = round((time.time() - start_time) * 1000)
                timer = read_from_memory(osu_process, timer_address)

                if time_timer > actions_list[action_iterator][0]:
                    click_and_move(playfield_monitor, actions_list[action_iterator])
                    if action_iterator != len(actions_list) - 1:
                        action_iterator += 1
                    else:
                        print('Конец маршрута повтора')
                        break

                if old_timer == timer:
                    iterator += 1
                else:
                    # print(timer, time_timer, time_timer - timer)
                    iterator = 0
            print('Конец цикла повтора')








if __name__ == '__main__':
    main()