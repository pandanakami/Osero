import os
import numpy as np
from my_module.osero_model import INPUT_CHANNEL
from my_module.osero_model import is_channel_first
from sklearn.model_selection import train_test_split


def load_data(input_dir: str):

    # 訓練データ
    (x_train, t_train) = _load_data_file(
        input_dir, "osero_train_x.npy", "osero_train_t.npy"
    )
    # 評価データ
    (x_eval, t_eval) = _load_data_file(
        input_dir, "osero_eval_x.npy", "osero_eval_t.npy"
    )
    # 評価データ(難しいやつ)
    (x_eval_difficult, t_eval_difficult) = _load_data_file(
        input_dir,
        "difficult_30_osero_eval_x.npy",
        "difficult_30_osero_eval_t.npy",
    )
    # 訓練データを検証データに分ける
    x_train, x_val, t_train, t_val = train_test_split(x_train, t_train, test_size=0.2)

    return (
        (x_train, t_train),
        (x_val, t_val),
        (x_eval, t_eval),
        (x_eval_difficult, t_eval_difficult),
    )


# 指定ファイルのX,Tを読み込む
def _load_data_file(input_dir: str, x_file, t_file):

    ## データ取得
    # (N,8,8)
    x = np.load(os.path.join(input_dir, x_file))

    # (N,1)
    t = np.load(os.path.join(input_dir, t_file)).astype(np.int32)

    if is_channel_first():
        # チャンネルが前
        def one_hot_encode(array):
            N, H, W = array.shape
            one_hot_array = np.zeros((N, INPUT_CHANNEL, H, W), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, c, :, :] = array == c
            return one_hot_array

        # (N,8,8) => (N,3,8,8)
        x = one_hot_encode(x)

    else:
        # チャンネルが後ろ
        def one_hot_encode(array):
            N, H, W = array.shape
            one_hot_array = np.zeros((N, H, W, INPUT_CHANNEL), dtype=np.int8)
            for c in range(3):
                one_hot_array[:, :, :, c] = array == c
            return one_hot_array

        # (N,8,8) => (N,8,8,3)
        x = one_hot_encode(x)

    return (x, t)
