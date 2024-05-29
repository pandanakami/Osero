import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout
import numpy as np

MODEL_NAME = "05_Simple"

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


def _conv(kernel_size, out_size, activation, is_padding=True, is_start=False):
    padding = "same" if is_padding else "valid"
    if is_start:
        return Conv2D(
            out_size,
            kernel_size=(kernel_size, kernel_size),
            activation=activation,
            input_shape=input_shape(),
            padding=padding,
            kernel_initializer=keras.initializers.he_normal,
        )
    else:
        return Conv2D(
            out_size,
            kernel_size=(kernel_size, kernel_size),
            activation=activation,
            padding=padding,
            kernel_initializer=keras.initializers.he_normal,
        )


def _dense(out_size, activation):
    return Dense(
        out_size,
        activation=activation,
        kernel_initializer=keras.initializers.he_normal,
    )


def get_model(DEBUG=False):
    # モデルの定義
    model = Sequential()

    # 畳み込み層
    model.add(_conv(3, 128, "relu", True, True))

    model.add(_conv(3, 128, "relu"))

    model.add(_conv(3, 128, "relu"))

    model.add(_conv(3, 128, "relu"))

    # model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Dropout(0.25))

    # フラット化
    model.add(Flatten())

    # 全結合層
    model.add(_dense(256, "relu"))

    model.add(_dense(128, "relu"))

    model.add(_dense(64, "relu"))

    # 出力層
    model.add(_dense(OUTPUT_SIZE, "softmax"))

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
