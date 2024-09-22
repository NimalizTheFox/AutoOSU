import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import keras
import tensorflow as tf


@tf.function
def compute_action(model: keras.Model, np_screenshots):
    result = model(np_screenshots)
    return result[0, :2], tf.argmax(result[0, 2:])


def create_model(input_image_shape, print_summary=False):
    model = keras.Sequential((
        keras.layers.Input(input_image_shape),
        keras.layers.Conv3D(32, (2, 4, 4), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Conv3D(64, (2, 4, 4), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dense(5, activation='relu')
    ))
    # Возможно сменить на tanh активации
    if print_summary:
        print(model.summary())

    model.compile(optimizer='adam',
                  loss='mean_squared_error',
                  metrics=['accuracy'])

    return model


if __name__ == '__main__':
    create_model((4, 60, 80, 1), True)
