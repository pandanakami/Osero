# ====================
# 学習サイクルの実行
# ====================

# パッケージのインポート

from self_play import self_play
from train_network import train_network
from evaluate_network import evaluate_network
from progress import Progress, ProgressState

# 進捗読む
progress = Progress.load()

for i in range(progress.loop_index, 10):
    print("Train", i, "====================")

    if progress.state == ProgressState.START:
        # セルフプレイ部
        self_play()
        progress.set_state(ProgressState.END_SELF_PLAY)

    if progress.state == ProgressState.END_SELF_PLAY:
        # パラメータ更新部
        train_network()
        progress.set_state(ProgressState.END_TRAIN)

    is_update = False
    if progress.state == ProgressState.END_TRAIN:
        # 新パラメータ評価部
        is_update = evaluate_network()
        progress.set_state(ProgressState.END_EVALUATE)

    # 強さチェック入れたい
    if is_update:
        pass

    progress.update_loop()
