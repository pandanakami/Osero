from keras.models import Sequential
from keras.layers import (
    MaxPooling2D,
    Flatten,
    Dropout,
    BatchNormalization,
)

from my_module.model import model_cmn
from my_module.model.model_cmn import conv, dense, model_debug_disp

MODEL_NAME = __name__

INPUT_CHANNEL = model_cmn.INPUT_CHANNEL
OSERO_HEIGHT = model_cmn.OSERO_HEIGHT
OSERO_WIDTH = model_cmn.OSERO_WIDTH
INPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH
OUTPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH + 1


def get_model(DEBUG=False):
    # モデルの定義
    model = Sequential()

    conv_activation = "relu"

    # 畳み込み層
    model.add(conv(3, 32, conv_activation, False, True))
    model.add(conv(3, 64, conv_activation, False))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))
    model.add(Flatten())

    # 全結合層
    model.add(dense(128, "relu"))
    model.add(dense(64, "relu"))

    # 出力層
    model.add(dense(OUTPUT_SIZE, "softmax"))

    # デバッグ
    if DEBUG:
        model_debug_disp(model)

    return model
