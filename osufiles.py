import os
import random
import struct
import time

import numpy as np
import zlib

OSU_PATH = r"D:\Games\osu!"
if not os.path.exists(OSU_PATH):
    OSU_PATH = r"C:\Games\osu!"


def create_topology():
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data\\osu_parse'):
        os.mkdir('data\\osu_parse')
    if not os.path.isdir('data\\records'):
        os.mkdir('data\\records')
    if not os.path.isfile('data\\song_list.txt'):
        open('data\\song_list.txt', 'w').close()


create_topology()


def get_song_list(osu_folder):
    """Возвращает все папки с песнями в osu!"""
    return tuple(os.listdir(osu_folder + r'\Songs'))
    # numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    # names = [" ".join(folder.split(' ')[1:]) for folder in song_list]


def sync_sort(a, b):
    """Сортируем по A, вместе с A сортируется и B"""
    # соединим два списка специальной функцией zip
    x = zip(a, b)

    # отсортируем, взяв первый элемент каждого списка как ключ
    xs = sorted(x, key=lambda tup: tup[0])

    # и последний шаг - извлечем
    a1 = [x[0] for x in xs]
    b1 = [x[1] for x in xs]
    return a1, b1


def get_songs_from_folders(osu_folder):
    """Смотрит все песни в папках песен и отсортирует по артистам"""
    song_list = get_song_list(osu_folder)
    # numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    names = [" ".join(folder.split(' ')[1:]).lower() for folder in song_list]

    names, song_list = sync_sort(names, song_list)
    song_dict = dict()
    for song_group in song_list:
        song_files = [file for file in os.listdir(osu_folder + '\\Songs\\' + song_group) if file.endswith(".osu")]
        song_dict[song_group] = [len(song_files), 0]
    return song_dict


def save_song_dict(song_dict):
    """Сохраняет словарь с песнями и количеством записанных повторов"""
    with open(r'data\song_list.txt', 'w') as file:
        for name, songs in song_dict.items():
            to_write = f'{name} {songs[1]}\n'
            file.write(to_write)


def read_song_dict():
    """Читает словарь с песнями и кол-вом записанных повторов"""
    song_dict = {}
    with open(r'data\song_list.txt', 'r') as file:
        song_dict_str_list = file.readlines()

    if len(song_dict_str_list) == 0:
        return {}

    for song_str in song_dict_str_list:
        record_num = int(song_str[song_str.rfind(' ') + 1:])
        name = song_str[:song_str.rfind(' ')]
        song_dict[name] = record_num
    return song_dict


def get_correct_song_dict(osu_folder):
    """Применяет информацию из файла к словарю песен из osu"""
    song_dict = get_songs_from_folders(osu_folder)  # Достаем инфу из osu
    from_file = read_song_dict()                    # Читаем записанное ранее
    for name, _ in song_dict.items():
        if name in from_file:
            song_dict[name][1] = from_file[name]    # Совмещаем знания
    return song_dict


def get_last_file(osu_folder):
    """Возвращает последний созданный файл или None, если файлов нет"""
    files = [os.path.join(osu_folder, f) for f in os.listdir(osu_folder)]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file


def save_record(record, path):
    """Сохраняет файл записи попутно его сжимая"""
    # каждый фрейм - [(скриншот), [корд1, корд2, действие]]
    result = struct.pack('i', len(record))

    frames_np = np.array([frame[0] for frame in record])
    result += frames_np.tobytes()

    actions_np = np.array([frame[1] for frame in record], dtype=np.float16)
    result += actions_np.tobytes()

    result_comp = zlib.compress(result, 3)  # Сжимаем запись

    with open(path, 'wb') as file:
        file.write(result_comp)
        file.flush()
    return path


def read_record(record_path, image_shape):
    """Читает файл записи и распаковывает его"""
    with open(record_path, 'rb') as f:
        record_file_comp = f.read()

    record_file = zlib.decompress(record_file_comp)
    length = struct.unpack('i', record_file[:4])[0]
    offset = 4

    frames_byte = record_file[offset:offset + 9600 * length]
    frames_np = np.frombuffer(frames_byte, np.float16).reshape((length, image_shape[1], image_shape[0], 1))
    offset += 9600 * length

    actions_byte = record_file[offset:]
    actions_np = np.frombuffer(actions_byte, np.float16).reshape((length, 3))

    record = [[frames_np[i], list(actions_np[i])] for i in range(length)]
    return record


def get_all_records():
    """Возвращает имена всех записей"""
    return os.listdir('data\\records')


def get_all_insane_records():
    """Возвращает имена всех записей"""
    record_list = os.listdir('data\\records')
    record_list = [record_list[i] for i in range(len(record_list))
                   if 'insane' in record_list[i].lower() or 'hard' in record_list[i].lower()]
    return record_list


def record_to_dataset(record):
    """Превращает запись в набор данных, который можно использовать в обучении модели"""
    dataset_x = []
    dataset_y = []
    np_frames = np.array([frame[0] for frame in record])
    actions_list = [frame[1] for frame in record]

    for i in range(4, len(np_frames) + 1):
        dataset_x.append(np_frames[i - 4: i])
        dataset_y.append(actions_list[i - 1])

    return dataset_x, dataset_y


def record_to_dataset_1_act(record):
    """Превращает запись в набор данных, который можно использовать в обучении модели"""
    np_frames = [frame[0] for frame in record]
    actions_list = [frame[1] for frame in record]
    actions_list = [[act[0], act[1], one_hot_encoding(act[2], 3)] for act in actions_list]

    ind0 = []
    ind1 = []
    ind2 = []
    for i in range(4, len(actions_list)):
        if actions_list[i][2][1] == 1:
            ind1.append(i)
        elif actions_list[i][2][2] == 1:
            ind2.append(i)
        else:
            ind0.append(i)

    # Обеспечиваем равномерность выборки
    act_len = int(len(ind1) * 1.5)

    random.shuffle(ind1)
    random.shuffle(ind2)
    random.shuffle(ind0)

    ind0 = ind0[:act_len]
    ind2 = ind2[:act_len]

    indexes = ind0 + ind1 + ind2

    dataset_x = []
    dataset_y = []
    for i in indexes:
        dataset_x.append(np.array(np_frames[i - 3: i + 1]))
        dataset_y.append(actions_list[i])
    return dataset_x, dataset_y


def one_hot_encoding(action, amount_actions):
    """Возвращает вектор из 0 и 1, где 1 - нужное действие по индексу aka One-Hot encoding"""
    return tuple([0 if i != action else 1 for i in range(amount_actions)])


def one_hot_decoding(action):
    """Превращает вектор из 0 и 1 в одно int значение, которое соответствует индексу единицы в списке"""
    return action.index(max(action))


def main():
    image_shape = (80, 60)
    # rec = read_record('data\\records\\Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal].comprec', image_shape)

    # song_dict = get_songs_from_folders(OSU_PATH)

    # record = read_record('data/Aimer - Through My Blood AM [Daybreak].comprec.comprec', image_shape)
    # print(record[100][1])
    # record[100][1][2] = one_hot_encoding(record[100][1][2], 3)
    # print(record[100][1])







if __name__ == '__main__':
    main()
