import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import keras


def create_model():
    model = keras.Sequential((
        keras.layers.Input((4, 80, 60, 1)),
        keras.layers.Conv3D(32, (2, 4, 4), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Conv3D(64, (2, 4, 4), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dense(3, activation='relu')
    ))
    print(model.summary())

    model.compile(optimizer='adam',
                  loss='mean_squared_error',
                  metrics=['accuracy'])


create_model()
