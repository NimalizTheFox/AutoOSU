import time

import osufiles
from captureosu import screenshot_standardization, get_frame, get_hwnd, get_playfield_monitor, get_window_text
from osucontrol import MenuController
from osuparser import get_osu_process, get_actions_list_from_replay, save_actions_list, read_actions_list
from replayRepeater import get_timer_address, read_from_memory, click_and_move


def get_replay_current_song(menu: MenuController, osu_process, timer_address, image_shape, hwnd, max_fps):
    min_frame_time = 1 / max_fps - 1 / 60

    record = []
    menu.autoplay_mod_on()
    menu.start_current_song()
    # menu.speedup_replay()
    while get_window_text(hwnd) == "osu!":
        time.sleep(0.01)
    print('Песня началась!')

    # Подгонка таймера
    timer = read_from_memory(osu_process, timer_address)
    old_timer = timer
    while timer <= 0 or old_timer == timer:
        old_timer = timer
        timer = read_from_memory(osu_process, timer_address)

    time_timer = 0
    start_time = time.time() - 0.015

    timer = read_from_memory(osu_process, timer_address)
    old_timer = timer
    while timer <= 15 or old_timer == timer:
        old_timer = timer
        timer = read_from_memory(osu_process, timer_address)
        time_timer = round((time.time() - start_time) * 1000)

    start_time += (time_timer - timer - 1) / 1000  # Система смещения, чтобы таймеры соответствовали друг-другу

    # Начало песни
    frames = 0
    while get_window_text(hwnd) != "osu!":  # Пока не появятся результаты
        start = time.time()

        time_timer = round((time.time() - start_time) * 1000)

        screenshot = get_frame(menu.playfield_monitor)
        record.append((screenshot_standardization(screenshot, image_shape), time_timer))
        frames += 1

        time.sleep(max(0., min_frame_time - (time.time() - start)))     # Обеспечение нужного фреймрейта

    time.sleep(3)
    menu.save_replay()          # Жмакаем f2, чтобы сохранить повтор
    menu.escape_from_results()  # Выходим в список песен
    print('Количество кадров:', frames)

    last_replay = osufiles.get_last_file(osufiles.OSU_PATH + r'\Replays')
    action_list = get_actions_list_from_replay(last_replay)     # Получаем список действий из повтора + обработка
    name = last_replay[last_replay.rfind('\\') + 8: -21]        # Поучаем название песни
    actions_path = rf'data\osu_parse\{name}.bin'
    save_actions_list(action_list, actions_path)                # И сохраняем в папку проекта
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


def vectorization_action(action, amount_actions):
    """Возвращает вектор из 0 и 1, где 1 - нужное действие по индексу"""
    return tuple([0 if i != action else 1 for i in range(amount_actions)])


def actions_processing(action_list, record, record_opt, action):
    """Вставка определенного действия из списка действий в соответствии с таймингами записи"""
    frame_i = 1
    act_iterator = 0
    finish = False
    # Проходимся вообще по всей траектории
    while act_iterator < len(action_list) and not finish:
        # Проходимся по всем action действиям
        while action_list[act_iterator][3] != action and not finish:
            # Пока есть action действия - двигаемся вперед
            if act_iterator < len(action_list) - 1:
                act_iterator += 1
            else:
                finish = True

        # Ищем ближайший фрейм к действию по таймингу
        while record[frame_i][1] < action_list[act_iterator][0] and not finish:
            if frame_i < len(record) - 1:
                frame_i += 1
            else:
                finish = True
        # Если действия или скриншоты не кончились, то записываем действия
        if not finish and record_opt[frame_i - 1][1] == 0:
            record_opt[frame_i - 1][1] = action_list[act_iterator][1:]

        act_iterator += 1
        frame_i += 1
    return record_opt


def record_processing(actions_path, record):
    """Пишет действия вместо временных меток и сохраняет"""
    print('\tПреобразование записи...')
    print('\r\t[0/5] Вытаскиваем действия из повтора...', end='')
    # record = [[(скрин_стандартизированный_np), таймер], [...]]
    record_opt = [[frame[0], 0] for frame in record]
    # изначально -  record_opt = [[(скрин_стандартизированный_np), 0], [...]]
    # в конце -     record_opt = [[(скрин_стандартизированный_np), [корд1, корд2, действие_в_векторе(1, 0, 0)]], [...]]

    action_list = read_actions_list(actions_path)
    # action_list = [[тайминг, корд1, корд2, действие], [...]]

    print(f'\r\t[1/5] Вычисляем векторы действий...{" "*20}', end='')
    for i in range(len(action_list)):
        action_list[i][3] = vectorization_action(action_list[i][3], 3)
    # action_list = [[тайминг, корд1, корд2, (действие_вект)], [...]]

    print(f'\r\t[2/5] Заполняем действия по таймингам 1/3...{" "*20}', end='')
    # Заполняем первые действия
    record_opt = actions_processing(action_list, record, record_opt, vectorization_action(1, 3))

    print(f'\r\t[2/5] Заполняем действия по таймингам 2/3...{" "*20}', end='')
    # Заполняем вторые действия
    record_opt = actions_processing(action_list, record, record_opt, vectorization_action(2, 3))

    print(f'\r\t[2/5] Заполняем действия по таймингам 3/3...{" "*20}', end='')
    # Заполняем нулевые действия
    record_opt = actions_processing(action_list, record, record_opt, vectorization_action(0, 3))

    print(f'\r\t[3/5] Заполняем пропуски...{" "*20}', end='')

    # Ставим на то, что последний фрейм это ничего не делание
    if record_opt[-1][1] == 0:
        record_opt[-1][1] = [0.5, 0.5, (1, 0, 0)]

    # Заполняем не заполненные фреймы нулями
    for i in range(len(record_opt) - 2, -1, -1):
        if record_opt[i][1] == 0:
            record_opt[i][1] = [record_opt[i + 1][1][0], record_opt[i + 1][1][1], (1, 0, 0)]

    print(f'\r\t[4/5] Сохраняем результат...', end='')
    # Убираем расширение файла и путь до файла, оставляем только имя песни
    name = actions_path[actions_path.rfind('\\') + 1: -4]
    osufiles.save_record(record_opt, name)

    print(f'\r\t[5/5] Готово!')


def main():
    """
    Запускаем osu.
    Переходим в список песен.
    Запускаем код.
    """
    max_fps = 30
    offsets = (0x8, 0x8, 0x3F4, 0xA4)   # Для версии b20241001
    image_shape = (80, 60)
    osu_folder = osufiles.OSU_PATH

    osu_process = get_osu_process(osu_folder)
    hwnd = get_hwnd()
    playfield_monitor = get_playfield_monitor(hwnd)

    timer_address = get_timer_address(osu_process, offsets) + offsets[-1]

    menu = MenuController(playfield_monitor, len(osufiles.get_song_list(osu_folder)))

    song_dict = osufiles.get_correct_song_dict(osu_folder)
    song_iterator = 0

    for name, songs in song_dict.items():
        start = songs[1]
        for i in range(start, songs[0]):
            print(f'Идем к песне [{name}], Записано: {i}/{songs[0]} вариаций')

            # Выбираем песню по координатам
            menu.choose_certain_song((song_iterator, i))

            # Запускаем запись
            actions_path, record = get_replay_current_song(menu, osu_process, timer_address, image_shape, hwnd, max_fps)
            record_processing(actions_path, record)

            # Запись об успехе обновляется
            song_dict[name][1] = i + 1
            osufiles.save_song_dict(song_dict)
        song_iterator += 1

    print('Все песни записаны!')


if __name__ == '__main__':
    main()
