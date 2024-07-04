# ====================
# 新パラメータ評価部
# ====================

# パッケージのインポート
from game import State
from pv_mcts import pv_mcts_action
from keras.models import load_model
from keras import backend as K
from pathlib import Path
from shutil import copy
import numpy as np
from path_mng import get_path, tqdm
from progress import Progress
import os

# パラメータの準備
EN_GAME_COUNT = 10  # 1評価あたりのゲーム数（本家は400）
EN_TEMPERATURE = 1.0  # ボルツマン分布の温度


# 先手プレイヤーのポイント
def first_player_point(ended_state):
    # 1:先手勝利, 0:先手敗北, 0.5:引き分け
    if ended_state.is_lose():
        return 0 if ended_state.is_first_player() else 1
    return 0.5


# 1ゲームの実行
def play(next_actions):
    # 状態の生成
    state = State()

    # tqdmオブジェクトを初期化
    pbar = tqdm(desc="GameCount", unit=" iteration", leave=False)
    try:
        # ゲーム終了までループ
        while True:
            # ゲーム終了時
            if state.is_done():
                break

            # 行動の取得
            next_action = (
                next_actions[0] if state.is_first_player() else next_actions[1]
            )
            action = next_action(state)

            # 次の状態の取得
            state = state.next(action)

            pbar.update(1)

    except KeyboardInterrupt:
        pbar.close()

    # 先手プレイヤーのポイントを返す
    return first_player_point(state)


# ベストプレイヤーの交代
def update_best_player():
    if os.path.exists(get_path("./model/best.h5")):
        # 1個だけバックアップ
        copy(get_path("./model/best.h5"), get_path("./model/best2.h5"))

    copy(get_path("./model/latest.h5"), get_path("./model/best.h5"))
    print("Change BestPlayer")


# ネットワークの評価
def evaluate_network(progress: Progress):
    # 最新プレイヤーのモデルの読み込み
    model0 = load_model(get_path("./model/latest.h5"))

    # ベストプレイヤーのモデルの読み込み
    model1 = load_model(get_path("./model/best.h5"))

    # PV MCTSで行動選択を行う関数の生成
    next_action0 = pv_mcts_action(model0, EN_TEMPERATURE)
    next_action1 = pv_mcts_action(model1, EN_TEMPERATURE)
    next_actions = (next_action0, next_action1)

    # 複数回の対戦を繰り返す
    total_point = 0
    for i in tqdm(range(EN_GAME_COUNT), desc="Evaluate", leave=False):
        # 1ゲームの実行
        if i % 2 == 0:
            total_point += play(next_actions)
        else:
            total_point += 1 - play(list(reversed(next_actions)))

    # 平均ポイントの計算
    average_point = total_point / EN_GAME_COUNT
    print("AveragePoint", average_point)
    progress.add_eval_result(average_point)

    # モデルの破棄
    K.clear_session()
    del model0
    del model1

    # ベストプレイヤーの交代
    if average_point > 0.5:
        update_best_player()
        return True
    else:
        return False


# 動作確認
if __name__ == "__main__":
    progress = Progress()
    evaluate_network(progress)
    progress.print()
