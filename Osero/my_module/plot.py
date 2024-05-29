import matplotlib.pyplot as plt


def plot(history):
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]

    # fig準備
    fig = plt.figure()
    # font
    plt.rc("font", family="serif")
    # plot
    plt.plot(range(len(loss)), loss, label="loss", color="black", linewidth=1)
    plt.plot(range(len(loss)), loss, label="loss", color="gray", linewidth=1)
    # ラベル
    plt.xlabel("epoch")
    plt.ylabel("loss")
    # 凡例
    plt.legend()
    # 描画
    plt.show()
