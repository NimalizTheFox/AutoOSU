import time

from osupyparser import OsuFile
from osupyparser import ReplayFile
import struct


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
    # pure_lzma = ReplayFile.from_file("test.osr", pure_lzma= True) This will return only lzma content.
    # data = ReplayFile.from_bytes(replay_files) you can also use pure bytes.
    # for d, e in info.items():
    #     print(f"{d}: {e}")  # Prints members of class.
    return info


def actions_list_to_file(actions_list, filename):
    with open(filename, 'wb') as f:
        for actions in actions_list:
            f.write(struct.pack('i 2f h', actions[0], actions[1], actions[2], actions[3]))


def actions_list_from_file(filename):
    actions_list = []
    with open(filename, 'rb') as f:
        while i1 := f.read(14):
            actions_list.append(struct.unpack('i 2f h', i1))
        f.close()
    return actions_list


def get_actions_list_from_replay(path_to_replay):
    full_data = parser_repls(path_to_replay)    # Получение полных данных реплея
    frames = full_data['frames']    # Получение действий из всех данных

    actions_list = []
    timer = -10     # Смещение таймера, иначе действие производится слишком поздно
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

    return actions_list


def main():
    path_rep = 'osu_repls/osu! - Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal] (2024-09-07) Osu.osr'
    # path_rep_2 = 'osu_repls/osu! - Nanakura Rin - Blouse [Normal] (2024-09-08) Osu.osr'


    actions_list = get_actions_list_from_replay(path_rep)
    print(len(actions_list))

    # Нужно сохранить в файл, чтобы каждый раз не трогать реплеи
    # 9 мс (Запись на диск - 7 мс, Чтение с диска - 1 мс), вместо 20 мс
    actions_list_to_file(actions_list, 'osu_parse/1.bin')       # Запись действий реплея на диск (~8мс на 1881 действие)
    file_actions_list = actions_list_from_file('osu_parse/1.bin')   # Чтение действий реплея (~1 мс на 1881 действий)
    print(len(file_actions_list))







if __name__ == '__main__':
    main()
