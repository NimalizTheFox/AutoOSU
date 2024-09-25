import os

import osufiles
from captureosu import *
from osucontrol import MenuController
from osuparser import get_osu_process, get_actions_list_from_replay, save_actions_list, read_actions_list
from replayRepeater import get_timer_address, read_from_memory, click_and_move


def get_replay_current_song(menu: MenuController, osu_process, timer_address):
    record = []
    menu.autoplay_mod_on()
    menu.start_current_song()
    # menu.speedup_replay()

    # Подгонка таймера
    timer = read_from_memory(osu_process, timer_address)
    while timer == 0:
        timer = read_from_memory(osu_process, timer_address)

    time_timer = 0
    start_time = time.time() - 0.015

    while timer <= 15:
        timer = read_from_memory(osu_process, timer_address)
        time_timer = round((time.time() - start_time) * 1000)

    start_time += (time_timer - timer - 1) / 1000  # Система смещения, чтобы таймеры соответствовали друг-другу

    # Начало, собсна, песни
    iterator = 0
    while iterator < 10:  # Пока таймер идет (смена занимает ~2000 чистых итераций)
        old_timer = timer
        time_timer = round((time.time() - start_time) * 1000)
        timer = read_from_memory(osu_process, timer_address)

        screenshot = get_frame(menu.playfield_monitor)
        record.append((screenshot, time_timer))

        if old_timer == timer:
            iterator += 1
        else:
            iterator = 0

    menu.save_replay()
    menu.escape_from_results()

    last_replay = osufiles.get_last_replay(osufiles.OSU_PATH + r'\Replays')
    action_list = get_actions_list_from_replay(last_replay)
    name = last_replay[last_replay.rfind('//') + 8: -21]
    actions_path = rf'data/osu_parse/{name}.bin'
    save_actions_list(action_list, actions_path)
    return actions_path, record


def record_repetition(menu: MenuController, actions_path, osu_process, timer_address):
    """Не используется из-за большого количества времени и сбивания рекордов"""
    actions_list = read_actions_list(actions_path)
    record = []

    menu.start_current_song()  # Начинаем песню

    # Подстройка таймера
    timer = read_from_memory(osu_process, timer_address)
    while timer == 0:
        timer = read_from_memory(osu_process, timer_address)

    time_timer = 0
    start_time = time.time() - 0.015

    while timer <= 15:
        timer = read_from_memory(osu_process, timer_address)
        time_timer = round((time.time() - start_time) * 1000)

    start_time += (time_timer - timer - 1) / 1000  # Система смещения, чтобы таймеры соответствовали друг-другу

    # ====== НАЧАЛО ПЕСНИ ======
    iterator = 0
    action_iterator = 0
    while iterator < 20:  # Пока таймер идет (смена занимает ~2000 чистых итераций)
        old_timer = timer
        time_timer = round((time.time() - start_time) * 1000)
        timer = read_from_memory(osu_process, timer_address)

        if time_timer > actions_list[action_iterator][0]:
            click_and_move(menu.playfield_monitor, actions_list[action_iterator])
            if action_iterator != len(actions_list) - 1:
                action_iterator += 1
            else:
                break

        screenshot = get_frame(menu.playfield_monitor)
        record.append((screenshot, time_timer))

        if old_timer == timer:
            iterator += 1
        else:
            iterator = 0
    return record


def record_processing(actions_path, record, image_shape):
    """Преобразует скриншоты и пишет действия вместо временных меток, плюс сохраняет"""
    record = [(screenshot_standardization(item[0], image_shape), item[1]) for item in record]
    record_opt = [[item[0], 0] for item in record]
    action_list = read_actions_list(actions_path)

    name = actions_path[actions_path.rfind('//') + 8: -21]

    frame_i = 1
    act_iterator = 0
    finish_1 = False
    while act_iterator < len(action_list) and not finish_1:
        while action_list[act_iterator][3] != 1 and not finish_1:
            if act_iterator < len(action_list) - 1:
                act_iterator += 1
            else:
                finish_1 = True

        while record[frame_i][1] < action_list[act_iterator][0] and not finish_1:
            if frame_i < len(record) - 1:
                frame_i += 1
            else:
                finish_1 = True

        if not finish_1:
            record_opt[frame_i - 1][1] = action_list[act_iterator][1:]

    frame_i = 1
    act_iterator = 0
    finish_2 = False
    while act_iterator < len(action_list) and not finish_2:
        while action_list[act_iterator][3] != 2 and not finish_2:
            if act_iterator < len(action_list) - 1:
                act_iterator += 1
            else:
                finish_2 = True

        while record[frame_i][1] < action_list[act_iterator][0] and not finish_2:
            if frame_i < len(record) - 1:
                frame_i += 1
            else:
                finish_2 = True

        if not finish_2 and record_opt[frame_i - 1] == 0:
            record_opt[frame_i - 1][1] = action_list[act_iterator][1:]

    frame_i = 1
    act_iterator = 0
    finish_0 = False
    while act_iterator < len(action_list) and not finish_0:
        while action_list[act_iterator][3] != 0 and not finish_0:
            if act_iterator < len(action_list) - 1:
                act_iterator += 1
            else:
                finish_0 = True

        while record[frame_i][1] < action_list[act_iterator][0] and not finish_0:
            if frame_i < len(record) - 1:
                frame_i += 1
            else:
                finish_0 = True

        if not finish_0 and record_opt[frame_i - 1] == 0:
            record_opt[frame_i - 1][1] = action_list[act_iterator][1:]
    osufiles.save_record(record_opt, name)   # Не доделано!
    # TODO: Доделать сохранение в osufiles.py









def main():
    offsets = (0x128, 0x58, 0x32C, 0xC64)   # Для версии b20240820.1
    image_shape = (80, 60)
    osu_folder = osufiles.OSU_PATH

    osu_process = get_osu_process(osu_folder)
    hwnd = get_hwnd()
    playfield_monitor = get_playfield_monitor(hwnd)

    timer_address = get_timer_address(osu_process, offsets) + offsets[-1]

    menu = MenuController(playfield_monitor, len(osufiles.get_song_list(osu_folder)))

    actions_path, record = get_replay_current_song(menu, osu_process, timer_address)
    # record = record_repetition(menu, actions_path, osu_process, timer_address)
    record_processing(actions_path, record, image_shape)









if __name__ == '__main__':
    main()