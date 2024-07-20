# ====================
# 学習サイクルの実行
# ====================
print("load start : train_cycle")

# パッケージのインポート
if __name__ == "__main__":
    from self_play import self_play
    from train_network import train_network
    from evaluate_network import evaluate_network
    from progress import Progress, ProgressState
    from play_with_old_othero import test_with_old_model
    from path_mng import tqdm
    import tensorflow as tf
    import os
    import myutil


def main():
    if myutil.is_windows():
        print("Running on CPU 0")
    else:
        print(f"Running on CPU: {os.sched_getaffinity(0)}")

    # 進捗読む
    progress = Progress.load()

    try:
        for i in range(progress.loop_index, 10):
            print(f"Train:{i} state:{progress.get_state()} ====================")

            if progress.get_state() == ProgressState.START:
                # セルフプレイ部
                self_play(progress)
                progress.set_state(ProgressState.END_SELF_PLAY)

            if progress.get_state() == ProgressState.END_SELF_PLAY:
                # パラメータ更新部
                train_network(i)
                progress.set_state(ProgressState.END_TRAIN)

                myutil.discord_write("osero rl::train finish!")
                if "END_WITH_TRAIN" in os.environ:
                    break

            is_update = False
            if progress.get_state() == ProgressState.END_TRAIN:
                # 新パラメータ評価部
                evaluate_network(progress)
                progress.set_state(ProgressState.END_EVALUATE)

            if progress.get_state() == ProgressState.END_EVALUATE:
                test_with_old_model(progress)
                progress.set_state(ProgressState.END_CHECK)

            progress.update_loop()

    except KeyboardInterrupt:
        print("Keyboard Interrupt.")


if __name__ == "__main__":
    main()

print("load end : train_cycle")
