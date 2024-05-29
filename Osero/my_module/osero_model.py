import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np

MODEL_NAME = "03_Simple"

INPUT_CHANNEL = 3
OSERO_HEIGHT = 8
OSERO_WIDTH = 8
INPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH
OUTPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH + 1


def is_channel_first():
    keras.backend.image_data_format() == "channels_first"


def input_shape():

    if is_channel_first():
        # チャンネルファースト
        return (INPUT_CHANNEL, OSERO_HEIGHT, OSERO_HEIGHT)
    else:
        # チャンネルラスト
        return (OSERO_HEIGHT, OSERO_HEIGHT, INPUT_CHANNEL)


def get_model(DEBUG=False):
    # モデルの定義
    model = Sequential()

    # 畳み込み層
    model.add(
        Conv2D(
            128,
            kernel_size=(3, 3),
            activation="relu",
            input_shape=input_shape(),
            padding="same",
            kernel_initializer=keras.initializers.he_normal,
        )
    )
    model.add(
        Conv2D(
            128,
            kernel_size=(3, 3),
            activation="relu",
            padding="same",
            kernel_initializer=keras.initializers.he_normal,
        )
    )
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Dropout(0.25))

    # フラット化
    model.add(Flatten())

    # 全結合層
    model.add(
        Dense(
            256,
            activation="relu",
            kernel_initializer=keras.initializers.he_normal,
        )
    )

    model.add(
        Dense(
            128,
            activation="relu",
            kernel_initializer=keras.initializers.he_normal,
        )
    )
    model.add(
        Dense(
            64,
            activation="relu",
            kernel_initializer=keras.initializers.he_normal,
        )
    )
    # 出力層
    model.add(
        Dense(
            OUTPUT_SIZE,
            activation="softmax",
            kernel_initializer=keras.initializers.he_normal,
        )
    )  # 盤面の各セルに対する確率

    if DEBUG:
        # レイヤー情報
        for i, layer in enumerate(model.layers):
            weights = layer.get_weights()
            s = f"[{i}] {layer.__class__}"
            if len(weights) == 0:
                s += ", "
            else:
                k = ""
                for j, o in enumerate(weights):
                    k += str(o.shape) + ", "
                s += f", weights_shape:{k}"
            print(f"{s}output_shape:{layer.output_shape}")

    return model
