import os
import struct
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
    if not os.path.isdir('data\\songs'):
        os.mkdir('data\\songs')


create_topology()


def get_song_list(osu_folder):
    """Возвращает все папки с песнями в osu!"""
    return tuple(os.listdir(osu_folder + r'\Songs'))
    # numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    # names = [" ".join(folder.split(' ')[1:]) for folder in song_list]


def save_song_list(song_list):
    """Сохраняет номера песен для последующей проверки на новинки"""
    numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    with open(r'data\song_list.bin', 'wb') as file:
        for number in numbers:
            file.write(struct.pack('i', number))


def get_old_song_list():
    """Читает номера песен из файла, если файла нет - возвращает пустоту"""
    if os.path.exists(r'data\song_list.bin'):
        number_list = []
        with open(r'data\song_list.bin', 'rb') as file:
            while i1 := file.read(4):
                number_list.append(struct.unpack('i', i1)[0])
            file.close()
        return tuple(number_list)
    else:
        return tuple([])


def check_new_songs(osu_folder):
    """Выдает True, если загружены новые песни, False, если новых нет"""
    song_list = get_song_list(osu_folder)
    new_numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    old_numbers = get_old_song_list()
    return len(set(new_numbers) - set(old_numbers)) > 0


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
        song_dict[song_group] = len(song_files)
    return song_dict


def get_last_file(osu_folder):
    """Возвращает последний созданный файл или None, если файлов нет"""
    files = [os.path.join(osu_folder, f) for f in os.listdir(osu_folder)]
    if not files:
        return None
    latest_file = max(files, key=os.path.getctime)
    return latest_file


def save_record(record, name):
    """Сохраняет файл записи попутно его сжимая"""
    # каждый фрейм - [(скриншот), [корд1, корд2, (вектор действий)]]
    result = struct.pack('i', len(record))
    for frame in record:
        result += frame[0].tobytes()
        result += struct.pack('2f 3B', frame[1][0], frame[1][1], frame[1][2][0], frame[1][2][1], frame[1][2][2])

    result_comp = zlib.compress(result, zlib.Z_BEST_COMPRESSION)    # Сжимаем запись

    with open(rf'data\records\{name}.comprec', 'wb') as file:
        file.write(result_comp)
        file.flush()
    return rf'data\records\{name}.comprec'


def read_record(record_path, image_shape):
    """Читает файл записи и распаковывает его"""
    with open(record_path, 'rb') as f:
        record_file_comp = f.read()

    record_file = zlib.decompress(record_file_comp)
    length = struct.unpack('i', record_file[:4])[0]

    record = []
    offset = 4
    for _ in range(length):
        record.append([
            np.frombuffer(record_file[offset:offset + 9600], np.float16).reshape((image_shape[1], image_shape[0], 1)),
            0
        ])
        offset += 9600
        temp = struct.unpack('2f 3B', record_file[offset:offset + 11])
        offset += 11
        record[-1][1] = [temp[0], temp[1], (temp[2], temp[3], temp[4])]
    return record


def main():
    image_shape = (80, 60)
    rec = read_record('data\\records\\Nanakura Rin (CV Hayami Saori) & Kitahama Eiji (CV Okamoto Nobuhiko) - Blouse [Normal].comprec', image_shape)


if __name__ == '__main__':
    main()
