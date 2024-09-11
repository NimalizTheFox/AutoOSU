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


def float_to_bytes(value):
    return struct.pack('f', value)


def bytes_to_float(value):
    return struct.unpack('f', value)


def actions_list_to_file(actions_list, filename):
    with open(filename, 'wb') as f:
        for actions in actions_list:
            f.write(struct.pack('i', actions[0]))
            f.write(struct.pack('2f', actions[1], actions[2]))
            f.write(struct.pack('h', actions[3]))


def actions_list_from_file(filename):
    actions_list = []
    with open(filename, 'rb') as f:
        while i1 := f.read(4):
            item = (
                struct.unpack('i', i1)[0],
                struct.unpack('f', f.read(4))[0],
                struct.unpack('f', f.read(4))[0],
                struct.unpack('h', f.read(2))[0]
            )
            actions_list.append(item)
        f.close()
    return actions_list


def get_actions_list_from_replay(path_to_replay):
    full_data = parser_repls(path_to_replay)
    frames = full_data['frames']

    actions_list = []
    timer = -10
    for frame in frames:
        timer += frame.delta
        actions_list.append((
            timer,
            frame.x / 512,
            frame.y / 384,
            frame.keys
        ))
    actions_list = [(0, 0.5, 0.5, 0)] + actions_list[2:]

    new_actions_list = [list(actions) for actions in actions_list]
    for i in range(1, len(actions_list)):
        if actions_list[i][3] > 0:
            if actions_list[i - 1][3] == actions_list[i][3] or actions_list[i + 1][3] == actions_list[i][3]:
                new_actions_list[i][3] = 2
            else:
                new_actions_list[i][3] = 1
        else:
            new_actions_list[i][3] = 0

    for i in range(len(new_actions_list) - 2, 0, -1):
        if new_actions_list[i][3] == 0:
            if new_actions_list[i - 1][3] != 2:
                new_actions_list[i][1] = new_actions_list[i + 1][1]
                new_actions_list[i][2] = new_actions_list[i + 1][2]

    actions_list = [[0, new_actions_list[1][1], new_actions_list[1][2], 0]]
    for i in range(1, len(new_actions_list) - 1):
        if new_actions_list[i][1:] != new_actions_list[i - 1][1:]:
            if new_actions_list[i][3] == 0:
                if new_actions_list[i - 1][3] == 2:
                    actions_list[-1][3] = 0
                    if new_actions_list[i + 1][3] == 0:
                        actions_list.append(new_actions_list[i + 1].copy())
                elif new_actions_list[i - 1][3] == 1:
                    actions_list.append(new_actions_list[i].copy())
                    actions_list[-1][0] = int(float((new_actions_list[i - 1][0] + new_actions_list[i + 1][0]) / 2))
            else:
                actions_list.append(new_actions_list[i].copy())

    actions_list.append([actions_list[-1][0] + 15, actions_list[-1][1], actions_list[-1][2], 0])

    return actions_list


def apply_resolution(playfield_monitor, actions_list):
    new_actions_list = []
    for action in actions_list:
        x = round(playfield_monitor['left'] + action[1] * playfield_monitor['width'])
        y = round(playfield_monitor['top'] + action[2] * playfield_monitor['height'])
        new_actions_list.append((action[0], x, y, action[3]))
    return new_actions_list


def main():
    # path_map = 'osu_maps/Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse (Fuxi66) [Normal].osu'
    # path_map = 'osu_maps/namirin - Ciel etoile (Hinsvar) [Hard].osu'
    path_rep = 'osu_repls/osu! - Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal] (2024-09-07) Osu.osr'
    # path_rep_2 = 'osu_repls/osu! - Nanakura Rin - Blouse [Normal] (2024-09-08) Osu.osr'

    # many_info = parser_map(path_map)

    # print("\n" * 2)
    # hit_objs = many_info['hit_objects']
    # for item in hit_objs[-10:]:
    #     print(item)

    actions_list = get_actions_list_from_replay(path_rep)
    print(len(actions_list))
    for _ in actions_list:
        print(_)


    # Нужно сохранить в файлик, чтобы каждый раз не трогать реплеи
    # actions_list_to_file(new_actions_list, 'osu_parse/1.bin')
    # file_actions_list = actions_list_from_file('osu_parse/1.bin')





if __name__ == '__main__':
    main()
