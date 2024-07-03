# ====================
# セルフプレイ部
# ====================

# パッケージのインポート
from game import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE
from datetime import datetime
from keras.models import load_model
from keras import backend as K
from pathlib import Path
import numpy as np
import pickle
import os
import sys
from tqdm import tqdm
from path_mng import get_path

# パラメータの準備
SP_GAME_COUNT = 500  # セルフプレイを行うゲーム数（本家は25000）
SP_TEMPERATURE = 1.0  # ボルツマン分布の温度パラメータ


# 先手プレイヤーの価値
def first_player_value(ended_state):
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if ended_state.is_lose():
        return -1 if ended_state.is_first_player() else 1
    return 0


# 学習データの保存
def write_data(history):
    now = datetime.now()
    os.makedirs(get_path("./data/"), exist_ok=True)  # フォルダがない時は生成
    path = get_path(
        "./data/{:04}{:02}{:02}{:02}{:02}{:02}.history".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second
        )
    )
    with open(path, mode="wb") as f:
        pickle.dump(history, f)


# 1ゲームの実行
def play(model):
    # 学習データ
    history = []

    # 状態の生成
    state = State()

    # tqdmオブジェクトを初期化
    pbar = tqdm(desc="GameCount", unit=" iteration", leave=False)

    try:
        while True:
            # ゲーム終了時
            if state.is_done():
                break

            # 合法手の確率分布の取得
            scores = pv_mcts_scores(model, state, SP_TEMPERATURE)

            # 学習データに状態と方策を追加
            policies = [0] * DN_OUTPUT_SIZE
            for action, policy in zip(state.legal_actions(), scores):
                policies[action] = policy
            history.append([[state.pieces, state.enemy_pieces], policies, None])

            # 行動の取得
            action = np.random.choice(state.legal_actions(), p=scores)

            # 次の状態の取得
            state = state.next(action)

            pbar.update(1)

    except KeyboardInterrupt:
        pbar.close()

    # 学習データに価値を追加
    value = first_player_value(state)
    for i in range(len(history)):
        history[i][2] = value
        value = -value
    return history


# セルフプレイ
def self_play():
    # 学習データ
    history = []

    # ベストプレイヤーのモデルの読み込み
    model = load_model(get_path("./model/best.h5"))

    # 複数回のゲームの実行
    try:
        for _ in tqdm(range(SP_GAME_COUNT), desc="PlayCount", leave=True):
            # 1ゲームの実行
            h = play(model)
            history.extend(h)
    except KeyboardInterrupt as e:
        raise e

    # 学習データの保存
    write_data(history)

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == "__main__":
    self_play()