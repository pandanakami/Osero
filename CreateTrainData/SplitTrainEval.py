import numpy as np
import os

PROTO_TRAIN_NUM = 100000


def split_train_eval():
    x_train_full = np.load("output/osero_train_full_x.npy")
    t_train_full = np.load("output/osero_train_full_t.npy")

    num = x_train_full.shape[0]
    train_num = int(np.floor(num * 0.8))
    eval_num = num - train_num

    x_train = x_train_full[:train_num, :, :]
    x_eval = x_train_full[train_num:, :, :]

    t_train = t_train_full[:train_num]
    t_eval = t_train_full[train_num:]

    os.makedirs("output", exist_ok=True)
    np.save("output/osero_train_x.npy", x_train)
    np.save("output/osero_eval_x.npy", x_eval)
    np.save("output/osero_train_t.npy", t_train)
    np.save("output/osero_eval_t.npy", t_eval)


def generate_proto_data():

    x_train_full = np.load("output/osero_train_full_x.npy")
    t_train_full = np.load("output/osero_train_full_t.npy")

    num = x_train_full.shape[0]
    train_num = PROTO_TRAIN_NUM
    eval_num = int(PROTO_TRAIN_NUM * 0.8)

    x_train = x_train_full[:train_num, :, :]
    x_eval = x_train_full[train_num : train_num + eval_num, :, :]

    t_train = t_train_full[:train_num]
    t_eval = t_train_full[train_num : train_num + eval_num]

    os.makedirs("output/proto", exist_ok=True)
    np.save("output/proto/osero_train_x.npy", x_train)
    np.save("output/proto/osero_eval_x.npy", x_eval)
    np.save("output/proto/osero_train_t.npy", t_train)
    np.save("output/proto/osero_eval_t.npy", t_eval)


# 難しいデータ生成
def generate_difficult_data():
    dataset = [
        ["output/osero_train_x.npy", "output/osero_train_t.npy"],
        ["output/osero_eval_x.npy", "output/osero_eval_t.npy"],
        ["output/proto/osero_train_x.npy", "output/proto/osero_train_t.npy"],
        ["output/proto/osero_eval_x.npy", "output/proto/osero_eval_t.npy"],
    ]
    for data in dataset:
        _generate_difficult_data(data[0], data[1])


# 難しいデータの閾値(置いたコマの数)
DIFFICULT_THRESHOLD = 30
DIFFICULT_PREFIX = "difficult_30_"


# 指定したデータの難しいデータ生成
def _generate_difficult_data(x_file, t_file):

    x = np.load(x_file)
    t = np.load(t_file)
    filter = _get_difficult_filter(x)
    x = x[filter]
    t = t[filter]

    x_name = DIFFICULT_PREFIX + os.path.basename(x_file)
    t_name = DIFFICULT_PREFIX + os.path.basename(t_file)
    dir = os.path.dirname(x_file)

    out_x_file = os.path.join(dir, x_name)
    out_t_file = os.path.join(dir, t_name)
    np.save(out_x_file, x)
    np.save(out_t_file, t)

    print(f"generate {out_x_file}, {out_t_file}")


# 指定したデータから難しいデータを抽出
def _get_difficult_filter(data):
    # 石が置かれている要素を抽出
    count_valid = np.sum(data > 0, axis=(1, 2))

    return np.where(count_valid >= DIFFICULT_THRESHOLD)[0]


if __name__ == "__main__":
    # split_train_eval()
    # generate_proto_data()
    generate_difficult_data()
