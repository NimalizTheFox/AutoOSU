import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import random
import numpy as np
import keras
import tensorflow as tf
from osufiles import get_all_records, read_record, record_to_dataset
from sklearn.model_selection import train_test_split


@tf.function
def compute_action(model: keras.Model, np_screenshots):
    result = model(np_screenshots)
    return tf.clip_by_value(result[0, :2], 0, 1), tf.argmax(result[0, 2:])


def create_model(input_image_shape, print_summary=False):
    model = keras.Sequential((
        keras.layers.Input(input_image_shape),
        keras.layers.Conv3D(32, (2, 4, 4), padding='same', activation='tanh'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Conv3D(64, (2, 4, 4), padding='same', activation='tanh'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='tanh'),
        keras.layers.Dense(5, activation='tanh')
    ))
    # Возможно сменить на tanh активации
    if print_summary:
        print(model.summary())

    # Метрика - косинусное сходство (вместо точности)
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=[keras.metrics.CosineSimilarity()])
    return model


def train_model_with_all_data(model: keras.Model, image_shape):
    records_fn = get_all_records()
    random.shuffle(records_fn)
    for offset in range(0, len(records_fn), 4):
        dataset_x = []  # Входные данные
        dataset_y = []  # Выходные данные
        current_names = records_fn[offset: offset + 4]  # Выбор данных
        print(f'Записи для обучения: {current_names}\nЧитаем записи [0/{len(current_names)}]', end='')
        iterator = 0
        for record_fn in current_names:
            record = read_record(f'data\\records\\{record_fn}', image_shape)    # Читаем запись
            temp_x, temp_y = record_to_dataset(record)  # Разбираем запись на датасет
            dataset_x += temp_x     # И дополняем входные и выходные данные в рамках этих 4 записей
            dataset_y += temp_y

            iterator += 1
            print(f'\rЧитаем записи [{iterator}/{len(current_names)}]', end='')

        dataset_x = np.array(dataset_x)
        dataset_y = np.array(dataset_y)
        print(f'\nЗаписи прочитаны!')

        # Делим выборку на обучающую и тестовую
        (trainX, testX, trainY, testY) = train_test_split(dataset_x, dataset_y, test_size=0.1)
        model.fit(trainX, trainY, validation_data=(testX, testY), epochs=2, batch_size=64)    # Проводим обучение
    model.save('model.keras')     # И сохраняем обученную модель


def load_model():
    return keras.models.load_model('model.keras')


def main():
    image_shape = (80, 60)
    input_image_shape = (4, image_shape[1], image_shape[0], 1)

    model = create_model(input_image_shape, True)
    train_model_with_all_data(model, image_shape)


if __name__ == '__main__':
    main()
