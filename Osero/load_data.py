import numpy as np
from osero_model import INPUT_CHANNEL, OUTPUT_SIZE
from osero_model import is_channel_first
from tensorflow import keras
from sklearn.model_selection import train_test_split


def load_data(TRAIN_INPUT_DIR: str):

    ## データ取得
    # (N,8,8)
    x_train = np.load(TRAIN_INPUT_DIR + "osero_train_x.npy")
    x_eval = np.load(TRAIN_INPUT_DIR + "osero_eval_x.npy")
    # (N,1)
    t_train = np.load(TRAIN_INPUT_DIR + "osero_train_t.npy")
    t_eval = np.load(TRAIN_INPUT_DIR + "osero_eval_t.npy")

    if is_channel_first():
        # チャンネルが前
        def one_hot_encode(array):
            N, H, W = array.shape
            one_hot_array = np.zeros((N, INPUT_CHANNEL, H, W), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, c, :, :] = array == c
            return one_hot_array

        # (N,8,8) => (N,3,8,8)
        x_train = one_hot_encode(x_train)
        x_eval = one_hot_encode(x_eval)

    else:
        # チャンネルが後ろ
        def one_hot_encode(array):
            N, H, W = array.shape
            one_hot_array = np.zeros((N, H, W, INPUT_CHANNEL), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, :, :, c] = array == c
            return one_hot_array

        # (N,8,8) => (N,8,8,3)
        x_train = one_hot_encode(x_train)
        x_eval = one_hot_encode(x_eval)

    t_train = keras.utils.to_categorical(t_train, OUTPUT_SIZE, dtype=np.float16)
    t_eval = keras.utils.to_categorical(t_eval, OUTPUT_SIZE, dtype=np.float16)

    # 訓練データを検証データに分ける
    x_train, x_val, t_train, t_val = train_test_split(x_train, t_train, test_size=0.2)

    return (x_train, t_train), (x_val, t_val), (x_eval, t_eval)
