import keras

import numpy as np
from my_module.model.model_cmn import is_channel_first, INPUT_CHANNEL
import my_module.osero_model_wrap as mw


def _one_hot(x):

    if is_channel_first():
        # チャンネルが前
        def one_hot_encode(array):
            H, W = array.shape
            one_hot_array = np.zeros((1, INPUT_CHANNEL, H, W), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, c, :, :] = array == c
            return one_hot_array

        # (8,8) => (1,3,8,8)
        x = one_hot_encode(x)

    else:
        # チャンネルが後ろ
        def one_hot_encode(array):
            H, W = array.shape
            one_hot_array = np.zeros((1, H, W, INPUT_CHANNEL), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, :, :, c] = array == c
            return one_hot_array

        # (8,8) => (1,8,8,3)
        x = one_hot_encode(x)

    return x


def pred(model: keras.models.Sequential, input):
    input = np.array(input)
    input = _one_hot(input)
    output = model.predict(input, verbose=0)
    return output.tolist()


def test2(model: keras.models.Sequential, input):
    import sys

    sys.stdout.write("aaa")

if __name__ == "__main__":
    data = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 0, 0, 0, 0],
        [0, 0, 0, 2, 2, 0, 0, 0],
        [0, 0, 0, 2, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    model = mw.load_model()
    y = pred(model, data)
    print(y)
