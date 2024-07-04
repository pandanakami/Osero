# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート

from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network
from progress import Progress, ProgressState
from play_with_old_othero import test_with_old_model
from path_mng import tqdm


def main():
    # 進捗読む
    progress = Progress.load()

    try:
        for i in range(progress.loop_index, 10):
            print("Train", i, "====================")

            if progress.get_state() == ProgressState.START:
                # セルフプレイ部
                self_play(progress)
                progress.set_state(ProgressState.END_SELF_PLAY)

            if progress.get_state() == ProgressState.END_SELF_PLAY:
                # パラメータ更新部
                train_network(i)
                progress.set_state(ProgressState.END_TRAIN)

            is_update = False
            if progress.get_state() == ProgressState.END_TRAIN:
                # 新パラメータ評価部
                evaluate_network()
                progress.set_state(ProgressState.END_EVALUATE)

            if progress.get_state() == ProgressState.END_EVALUATE:
                test_with_old_model(progress)
                progress.set_state(ProgressState.END_CHECK)

            progress.update_loop()

    except KeyboardInterrupt:
        print("Keyboard Interrupt.")


if __name__ == "__main__":
    main()
