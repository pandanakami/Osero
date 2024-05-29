import numpy as np


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

    np.save("output/osero_train_x.npy", x_train)
    np.save("output/osero_eval_x.npy", x_eval)
    np.save("output/osero_train_t.npy", t_train)
    np.save("output/osero_eval_t.npy", t_eval)


if __name__ == "__main__":
    split_train_eval()
