import matplotlib.pyplot as plt


def plot(history, savepos, display_fig, save_fig):
    # history構造直す
    epochs = [item["epoch"] for item in history]
    loss = [item["loss"] for item in history]
    val_loss = [item["val_loss"] for item in history]

    accuracy = [item["accuracy"] for item in history]
    val_accuracy = [item["val_accuracy"] for item in history]

    # グラフの作成
    fig, ax1 = plt.subplots()

    # ラベル
    ax1.set_xlabel("Epoch")

    # 左側のy軸（loss）
    ax1.set_ylabel("Loss", color="tab:blue")
    ax1.plot(epochs, loss, label="Training Loss", color="tab:blue")
    ax1.plot(
        epochs, val_loss, label="Validation Loss", linestyle="--", color="tab:blue"
    )
    ax1.tick_params(axis="y", labelcolor="tab:blue")

    # 右側のy軸（accuracy）
    ax2 = ax1.twinx()
    ax2.set_ylabel("Accuracy", color="tab:orange")
    ax2.plot(epochs, accuracy, label="Training Accuracy", color="tab:orange")
    ax2.plot(
        epochs,
        val_accuracy,
        label="Validation Accuracy",
        linestyle="--",
        color="tab:orange",
    )
    ax2.tick_params(axis="y", labelcolor="tab:orange")

    # 凡例
    fig.legend(loc="upper left", bbox_to_anchor=(0.1, 0.9))
    fig.tight_layout()
    plt.title("Training and Validation Loss and Accuracy")

    if display_fig:
        # 描画
        plt.show()

    if save_fig:
        plt.savefig(savepos)
