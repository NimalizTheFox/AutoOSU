import keras


def create_model_cord(input_image_shape, print_summary=False):
    model = keras.Sequential((
        keras.layers.Input(input_image_shape),
        keras.layers.Conv3D(32, (2, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Conv3D(64, (2, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Conv3D(128, (1, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((1, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(256, activation='relu'),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(100, activation='relu'),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(2, activation='relu')
    ))
    if print_summary:
        print(model.summary())

    # Метрика - R2 - максимум 1, 0 - случайное распределение, меньше 0 - хуже случайного
    model.compile(optimizer='adam', loss='mean_absolute_error', metrics=['accuracy'])
    return model


def create_model_act(input_image_shape, print_summary=False):
    model = keras.Sequential((
        keras.layers.Input(input_image_shape),
        keras.layers.Conv3D(64, (2, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Conv3D(128, (2, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((2, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Conv3D(256, (1, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((1, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Conv3D(512, (1, 3, 3), padding='same', activation='relu'),
        keras.layers.MaxPool3D((1, 2, 2), strides=2),
        keras.layers.Dropout(0.1),
        keras.layers.Flatten(),
        keras.layers.Dense(512, activation='relu'),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(100, activation='relu'),
        keras.layers.Dropout(0.4),
        keras.layers.Dense(3, activation='softmax')
    ))
    # 'leaky_relu'
    # keras.layers.PReLU
    if print_summary:
        print(model.summary())

    # Метрика - косинусное сходство (вместо точности)
    # model.compile(optimizer='adam', loss=keras.losses.CategoricalFocalCrossentropy(), metrics=['accuracy'])
    model.compile(optimizer='adam', loss=keras.losses.CategoricalCrossentropy(), metrics=['accuracy'])
    return model


def create_callbacks(stop_fit_patience=6, lr_up=False, lr_down=True, max_lr=0.002,
                     min_lr=3e-5, lr_up_factor=1.2, lr_down_factor=0.7, print_checkpoints=True):
    """
    Создает обратные вызовы для улучшения обучения моделей и облегчения работы с ними
    :param stop_fit_patience: Через сколько эпох остановить обучение, если точность тестовой выборки не растет
    :param lr_up: Включать ли повышение learning rate
    :param lr_down: Включать ли понижение learning rate
    :param max_lr: Максимальный LR
    :param min_lr: Минимальный LR
    :param lr_up_factor: lr = lr * factor
    :param lr_down_factor: lr = lr * factor
    :param print_checkpoints: Выводить ли сообщения о чекпоинтах
    :return: Список обратных вызовов, которые нужно применить к обучению
    """
    early_stop = keras.callbacks.EarlyStopping(
        monitor='val_accuracy',
        min_delta=0,
        patience=stop_fit_patience,
        restore_best_weights=True)

    lr_upper = keras.callbacks.LearningRateScheduler(
        schedule=lambda epoch, lr: lr if epoch < 1 else max(min(float(lr * lr_up_factor), max_lr), min_lr))

    lr_downer = keras.callbacks.ReduceLROnPlateau(
        monitor='val_loss',
        # factor=0.58,
        factor=lr_down_factor,
        patience=0,
        min_delta=-0.0001,
        min_lr=min_lr)

    checkpoint_act = keras.callbacks.ModelCheckpoint(
        filepath='checkpoint_act.keras',
        monitor='val_accuracy',
        mode='max',
        save_best_only=True,
        verbose=1 if print_checkpoints else 0)

    checkpoint_cord = keras.callbacks.ModelCheckpoint(
        filepath='checkpoint_cord.keras',
        monitor='val_accuracy',
        mode='max',
        save_best_only=True,
        verbose=1 if print_checkpoints else 0)

    callbacks_act = [early_stop, checkpoint_act]
    callbacks_cord = [early_stop, checkpoint_cord]

    if lr_up:
        callbacks_act.append(lr_upper)
        callbacks_cord.append(lr_upper)
    if lr_down:
        callbacks_act.append(lr_downer)
        callbacks_cord.append(lr_downer)

    return callbacks_cord, callbacks_act
