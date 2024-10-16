import time
import windows
from osupyparser import OsuFile, ReplayFile
import struct
import os

def parser_map(path: str):
    """Нужен .osu файл"""
    data = OsuFile(path).parse_file()
    info = data.__dict__
    for d, e in info.items():
        print(f"{d}: {e}")  # Prints all members of the class.
    return info


def parser_repls(path: str):
    """Нужен .osr файл"""
    data = ReplayFile.from_file(path)
    info = data.__dict__
    return info


def save_actions_list(actions_list, filename):
    with open(filename, 'wb') as f:
        for actions in actions_list:
            f.write(struct.pack('i 2f h', actions[0], actions[1], actions[2], actions[3]))


def read_actions_list(filename):
    actions_list = []
    with open(filename, 'rb') as f:
        while i1 := f.read(14):
            actions_list.append(list(struct.unpack('i 2f h', i1)))
        f.close()
    return actions_list


def get_actions_list_from_replay(path_to_replay):
    """Получение маршрута из повтора, +обработка маршрута для оптимизации траекторий"""
    full_data = parser_repls(path_to_replay)    # Получение полных данных повтора
    frames = full_data['frames']    # Получение действий из всех данных

    actions_list = []
    timer = -20     # Смещение таймера, иначе действие производится слишком поздно
    for frame in frames:
        timer += frame.delta
        actions_list.append((
            timer,
            frame.x / 512,  # Перевод координат в [0..1]
            frame.y / 384,  # Перевод координат в [0..1]
            frame.keys
        ))
    actions_list = [(0, 0.5, 0.5, 0)] + actions_list[2:]    # Полный реплей

    new_actions_list = [list(actions) for actions in actions_list]
    for i in range(1, len(actions_list)):   # Изменение клавиш на одиночные и длительные нажатия
        if actions_list[i][3] > 0:
            if actions_list[i - 1][3] == actions_list[i][3] or actions_list[i + 1][3] == actions_list[i][3]:
                new_actions_list[i][3] = 2  # Долгое нажатие
            else:
                new_actions_list[i][3] = 1  # Одиночное нажатие
        else:
            new_actions_list[i][3] = 0  # Не требует нажатий

    for i in range(len(new_actions_list) - 2, 0, -1):   # Изменение позиции нулей на позицию следующего нажатия
        if new_actions_list[i][3] == 0 and new_actions_list[i - 1][3] != 2:
            new_actions_list[i][1] = new_actions_list[i + 1][1]
            new_actions_list[i][2] = new_actions_list[i + 1][2]

    actions_list = [[0, new_actions_list[1][1], new_actions_list[1][2], 0]]
    for i in range(1, len(new_actions_list) - 1):
        # Отчистка нулей, которые повторяют положение предыдущих (почти все из-за предыдущего шага)
        if new_actions_list[i][1:] != new_actions_list[i - 1][1:]:
            if new_actions_list[i][3] == 0:
                if new_actions_list[i - 1][3] == 2:
                    actions_list[-1][3] = 0
                    if new_actions_list[i + 1][3] == 0:
                        actions_list.append(new_actions_list[i + 1].copy())
                elif new_actions_list[i - 1][3] == 1:
                    actions_list.append(new_actions_list[i].copy())
                    # Изменение 0, стоящих после 1 (+ половина времени до следующего действия)
                    actions_list[-1][0] = int(float((new_actions_list[i - 1][0] + new_actions_list[i + 1][0]) / 2))
            else:
                actions_list.append(new_actions_list[i].copy())

    actions_list.append([actions_list[-1][0] + 15, actions_list[-1][1], actions_list[-1][2], 0])
    # Удалить половину или две трети всех двоек, они не нужны для работы, но занимают цикл

    os.remove(path_to_replay)       # Удаляем повтор, чтобы не путать последующие запуски

    return actions_list


def get_osu_process(osu_folder):
    """Возвращает хендлер процесса osu! для таймера, если нет процесса, то запускает osu!"""
    osu_process = None
    process_name = "osu!.exe"
    while osu_process is None:
        process_list = windows.system.enumerate_processes()
        for process in process_list:
            if process.name == process_name:
                osu_process = process
                break
        if osu_process is None:
            os.startfile(osu_folder + '\\osu!.exe')
            time.sleep(2)
    return osu_process


def main():
    path_rep = 'osu_repls/osu! - Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal] (2024-09-07) Osu.osr'
    # path_rep_2 = 'osu_repls/osu! - Nanakura Rin - Blouse [Normal] (2024-09-08) Osu.osr'


    actions_list = get_actions_list_from_replay(path_rep)
    print(len(actions_list))

    # Нужно сохранить в файл, чтобы каждый раз не трогать реплеи
    # 9 мс (Запись на диск - 7 мс, Чтение с диска - 1 мс), вместо 20 мс
    save_actions_list(actions_list, 'osu_parse/1.bin')       # Запись действий реплея на диск (~8мс на 1881 действие)
    file_actions_list = read_actions_list('osu_parse/1.bin')   # Чтение действий реплея (~1 мс на 1881 действий)
    print(len(file_actions_list))







if __name__ == '__main__':
    main()
