import matplotlib.pyplot as plt


def plot(history, savepos):
    # history構造直す
    loss = [item["loss"] for item in history]
    val_loss = [item["val_loss"] for item in history]

    # fig準備
    fig = plt.figure()
    # font
    plt.rc("font", family="serif")
    # plot
    plt.plot(range(len(loss)), loss, label="loss", color="black", linewidth=1)
    plt.plot(
        range(len(val_loss)), val_loss, label="val_loss", color="gray", linewidth=1
    )
    # ラベル
    plt.xlabel("epoch")
    plt.ylabel("loss")
    # 凡例
    plt.legend()
    # 描画
    # plt.show()
    plt.savefig(savepos)
