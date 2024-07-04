# ====================
# セルフプレイ部
# ====================

print("load start : self_play")

# パッケージのインポート
from datetime import datetime
from keras.models import load_model, Model, clone_model
from keras import backend as K
from pathlib import Path
import numpy as np
import pickle
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import Manager
import time

from game import State
from pv_mcts import pv_mcts_scores
from dual_network import DN_OUTPUT_SIZE, dual_network
from path_mng import get_path, tqdm, is_colab
from progress import Progress


# パラメータの準備
SP_GAME_COUNT = 1000  # セルフプレイを行うゲーム数（本家は25000）
SP_TEMPERATURE = 1.0  # ボルツマン分布の温度パラメータ

if is_colab():
    MULTI_TASK_NUM = os.cpu_count()
else:
    MULTI_TASK_NUM = 2


# 先手プレイヤーの価値
def first_player_value(ended_state):
    # 1:先手勝利, -1:先手敗北, 0:引き分け
    if ended_state.is_lose():
        return -1 if ended_state.is_first_player() else 1
    return 0


# 学習データの保存
def write_data(history):
    now = datetime.now()
    os.makedirs(get_path("./game_history/"), exist_ok=True)  # フォルダがない時は生成
    path = get_path(
        "./game_history/{:04}{:02}{:02}{:02}{:02}{:02}.history".format(
            now.year, now.month, now.day, now.hour, now.minute, now.second
        )
    )
    with open(path, mode="wb") as f:
        pickle.dump(history, f)


SIGNAL_RUN = 0
SIGNAL_WAIT = 1
SIGNAL_END = 2
SIGNAL_END_REQ = 3


# 1ゲームの実行
def game_play(
    model: Model,
    identifier: int,
    progress_list: list,
    signal_list: list,
):
    print(f":::::::({identifier})")

    # ベストプレイヤーのモデルの読み込み
    path = get_path("./model/best.h5")
    if not os.path.exists(path):
        dual_network()

    model = load_model(path)

    try:
        while True:
            if signal_list[identifier] == SIGNAL_WAIT:
                time.sleep(1)
                continue
            elif signal_list[identifier] == SIGNAL_END:
                del model
                return None

            # SIGNAL_RUN
            print(f"Game Play Start({identifier})")
            # 学習データ
            history = []

            # 状態の生成
            state = State()

            progress_list[identifier] = 0

            while True:
                if signal_list[identifier] == SIGNAL_END:
                    del model
                    return None

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

                progress_list[identifier] += 1

            # 学習データに価値を追加
            value = first_player_value(state)
            for i in range(len(history)):
                history[i][2] = value
                value = -value

            # 受け渡し用ファイル保存
            with open(f"tmp_history{identifier}.pkl", "wb") as f:
                pickle.dump(history, f)

            # 完了フラグ
            signal_list[identifier] = SIGNAL_WAIT
            history.clear()

    except KeyboardInterrupt:
        signal_list[identifier] = SIGNAL_END_REQ
        del model
        return None

    return None


# モデルのコピーを作成
def _create_model_copy(model: Model) -> Model:
    model_copy = clone_model(model)
    model_copy.set_weights(model.get_weights())
    return model_copy


# セルフプレイ
def self_play(progress: Progress):
    # 学習データ
    history = []

    # ベストプレイヤーのモデルの読み込み
    path = get_path("./model/best.h5")
    if not os.path.exists(path):
        dual_network()

    model = load_model(path)
    path = ""

    # 履歴をリストア
    path = get_path("game_history_tmp.pkl")
    if os.path.exists(path):
        with open(path, "rb") as f:
            history = pickle.load(f)
    initial_count = progress.play_count
    print(f"play start at :{initial_count}, history num:{len(history)}")

    progress_list = []
    copy_models = []
    tqdm_list = []
    for i in range(MULTI_TASK_NUM):
        copy_models.append(_create_model_copy(model))
        tqdm_list.append(tqdm(desc=f"GameCount{i}", unit=" iteration", leave=False))

    try:
        with Manager() as manager:
            progress_list = manager.list([0] * MULTI_TASK_NUM)
            signal_list = manager.list([SIGNAL_RUN] * MULTI_TASK_NUM)

            with tqdm(
                total=SP_GAME_COUNT,
                initial=initial_count,
                desc="PlayCount",
                leave=True,
            ) as pbar:

                with ProcessPoolExecutor(max_workers=MULTI_TASK_NUM) as executor:

                    count = initial_count

                    # 非同期プレイ開始
                    futures = [
                        executor.submit(
                            game_play, copy_models[i], i, progress_list, signal_list
                        )
                        for i in range(MULTI_TASK_NUM)
                    ]
                    # 非同期実行中
                    while any(future.running() for future in futures):
                        if -1 in progress_list:
                            raise KeyboardInterrupt()
                        # 進捗バー
                        for i in range(MULTI_TASK_NUM):
                            tqdm_list[i].n = progress_list[i]
                            tqdm_list[i].refresh()
                        # 中断チェック
                        endflag = False
                        if SIGNAL_END_REQ in signal_list:
                            endflag = True
                        else:
                            # 状態
                            for i in range(MULTI_TASK_NUM):
                                # 完了
                                if signal_list[i] == SIGNAL_WAIT:
                                    # 履歴をファイルから受け取り
                                    with open(f"tmp_history{i}.pkl", "rb") as f:
                                        h = pickle.load(f)
                                        history.extend(h)
                                    # テンポラリ保存
                                    with open(path, "wb") as f:
                                        pickle.dump(history, f)
                                    progress.update_play_count()
                                    print(
                                        f"end play. current history num:{len(history)}"
                                    )
                                    count += 1

                                    # 受け取り完了設定
                                    os.remove(f"tmp_history{i}.pkl")

                                    if count >= SP_GAME_COUNT:
                                        # 終了
                                        endflag = True
                                    else:
                                        # 継続
                                        signal_list[i] = SIGNAL_RUN
                        if endflag:
                            for i in range(MULTI_TASK_NUM):
                                signal_list[i] = SIGNAL_END
                        time.sleep(1)

    except KeyboardInterrupt as e:
        for p in tqdm_list:
            p.close()
        raise e

    # 学習データの保存
    write_data(history)

    # テンポラリ削除
    if os.path.exists(path):
        os.remove(path)

    # モデルの破棄
    K.clear_session()
    del model


# 動作確認
if __name__ == "__main__":
    self_play()


print("load end : self_play")
