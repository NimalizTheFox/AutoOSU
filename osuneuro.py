import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import random
import numpy as np
import keras
import tensorflow as tf
from osufiles import get_all_records, read_record, record_to_dataset_1_act, record_to_dataset, get_all_insane_records
from sklearn.model_selection import train_test_split
import models


@tf.function
def compute_action_cord(model: keras.Model, np_screenshots):
    result = model(np_screenshots)
    return tf.clip_by_value(result[0], 0, 1)


@tf.function
def compute_action_act(model: keras.Model, np_screenshots):
    result = model(np_screenshots)
    return tf.argmax(result[0])


def train_model_on_random_data(input_image_shape, image_shape, numer_of_data):
    # records_fn = get_all_records()
    records_fn = get_all_insane_records()
    random.shuffle(records_fn)
    current_names = records_fn[:numer_of_data]

    dataset_x = []  # Входные данные
    dataset_y = []  # Выходные данные
    iterator = 0
    print(f'Записи для обучения: {current_names}\nЧитаем записи [0/{len(current_names)}]', end='')
    for record_fn in current_names:
        record = read_record(f'data/records/{record_fn}', image_shape)  # Читаем запись
        temp_x, temp_y = record_to_dataset_1_act(record)  # Разбираем запись на датасет по первому действию
        dataset_x += temp_x  # И дополняем входные и выходные данные в рамках этих 4 записей
        dataset_y += temp_y
        del record

        iterator += 1
        print(f'\rЧитаем записи [{iterator}/{len(current_names)}]', end='')

    dataset_x = np.array(dataset_x)
    dataset_y_cord = [[item[0], item[1]] for item in dataset_y]
    dataset_y_cord = np.array(dataset_y_cord)
    dataset_y_act = [item[2] for item in dataset_y]
    dataset_y_act = np.array(dataset_y_act)
    print(f'\nЗаписи прочитаны!')

    # ========== УСЛОВИЯ ==========
    callbacks_act, callbacks_cord = models.create_callbacks(min_lr=1e-5)

    # ========== ОБУЧЕНИЕ ==========
    # === Координаты ===
    # model_cord = create_model_cord(input_image_shape, True)
    model_cord = load_model('checkpoint_cord.keras')
    (trainX, testX, trainY, testY) = train_test_split(dataset_x, dataset_y_cord, test_size=0.2)
    model_cord.fit(trainX, trainY, validation_data=(testX, testY), epochs=50, callbacks=callbacks_cord, batch_size=16)    # Проводим обучение
    model_cord.save('model_cord.keras')     # И сохраняем обученную модель

    # === Действие ===
    # (trainX, testX, trainY, testY) = train_test_split(dataset_x, dataset_y_act, test_size=0.2)
    # # model_act = create_model_act(input_image_shape, True)
    # model_act = load_model('checkpoint_act.keras')
    # model_act.fit(trainX, trainY, validation_data=(testX, testY), epochs=50, callbacks=callbacks, batch_size=50)    # Проводим обучение
    # model_act.save('model_act.keras')     # И сохраняем обученную модель

    # model_act = load_model('model_act.keras')

    # Проверка на тестовых данных
    ttt = testX[:10]
    yyy = testY[:10]
    # some_data = model_act.predict(ttt)
    some_data = model_cord.predict(ttt)
    # Показать как выглядят данные
    for i in range(len(ttt)):
        print(yyy[i], int(tf.argmax(yyy[i])), int(tf.argmax(some_data[i])), some_data[i])


def load_model(fn):
    return keras.models.load_model(fn)


def main():
    image_shape = (80, 60)
    input_image_shape = (4, image_shape[1], image_shape[0], 1)

    # model = create_model_act(input_image_shape, True)
    # train_model_with_all_data(model, image_shape)
    train_model_on_random_data(input_image_shape, image_shape, 20)






if __name__ == '__main__':
    main()
