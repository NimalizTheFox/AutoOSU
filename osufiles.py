import os
import struct


def create_topology():
    if not os.path.isdir('data'):
        os.mkdir('data')
    if not os.path.isdir('data/osu_parse'):
        os.mkdir('data/osu_parse')
    if not os.path.isdir('data/records'):
        os.mkdir('data/records')
    if not os.path.isdir('data/songs'):
        os.mkdir('data/songs')


create_topology()


def get_song_list(osu_folder):
    """Возвращает все папки с песнями в osu!"""
    return tuple(os.listdir(osu_folder + r'/Songs'))
    # numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    # names = [" ".join(folder.split(' ')[1:]) for folder in song_list]


def save_song_list(song_list):
    """Сохраняет номера песен для последующей проверки на новинки"""
    numbers = [int(folder_name.split(' ')[0]) for folder_name in song_list]
    with open(r'data/song_list.bin', 'wb') as file:
        for number in numbers:
            file.write(struct.pack('i', number))


def get_old_song_list():
    """Читает номера песен из файла, если файла нет - возвращает пустоту"""
    if os.path.exists(r'data/song_list.bin'):
        number_list = []
        with open(r'data/song_list.bin', 'rb') as file:
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
        song_files = [file for file in os.listdir(osu_folder + '/Songs/' + song_group) if file.endswith(".osu")]
        song_dict[song_group] = len(song_files)
    return song_dict



def main():
    OSU_PATH = r"D:\Games\osu!"
    if not os.path.exists(OSU_PATH):
        OSU_PATH = r"C:\Games\osu!"

    song_dict = get_songs_from_folders(OSU_PATH)
    for d, e in song_dict.items():
        print(f"{d}: {e}")


if __name__ == '__main__':
    main()
