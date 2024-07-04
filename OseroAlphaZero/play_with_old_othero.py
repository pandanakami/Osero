import sys

sys.path.append("../Osero")
import keras.backend as K
from keras.models import Model, load_model
import my_module.osero_model_wrap as mw
import numpy as np
import osero_pred
from pv_mcts import pv_mcts_scores
from pv_mcts import predict as mcts_predict
from path_mng import get_path
from enum import Enum
from game import State, BOARD_WIDTH, BOARD_SIZE
import copy
from tqdm import tqdm
import math
from progress import Progress, VsOldModelResult
from evaluate_network import EN_GAME_COUNT

old_model: Model = None
new_model: Model = None


def load_old_model():
    global old_model, new_model
    old_model = mw.load_model()
    new_model = load_model(get_path("./model/best.h5"))


class Turn(Enum):
    OLD_MODEL = 0
    NEW_MODEL = 1


W = 1
B = 2

S = 1
O = 2


# 0:旧モデルの勝ち
# 1:新モデルの勝ち
def play(old_is_first: bool, new_policy_func, disp_log=False) -> Turn:
    global old_model, new_model

    data = [
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, W, B, 0, 0, 0],
        [0, 0, 0, B, W, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]

    turn = Turn.OLD_MODEL if old_is_first else Turn.NEW_MODEL
    oldModelColor = 2 if old_is_first else 1
    newModelColor = 1 if old_is_first else 2

    count = 4
    pass_count = 0

    progress = tqdm(desc="StateCount", unit=" iteration", leave=False)

    while True:
        if pass_count == 2:
            break
        if count == BOARD_SIZE:
            break
        progress.update(1)

        if turn == Turn.OLD_MODEL:

            _data = copy.deepcopy(data)
            if old_is_first:
                for j in range(BOARD_WIDTH):
                    for i in range(BOARD_WIDTH):
                        if data[j][i] == W:
                            _data[j][i] = O
                        elif data[j][i] == B:
                            _data[j][i] = S
                        else:
                            _data[j][i] = 0
            else:
                _data = data
            pred = osero_pred.pred(old_model, _data)
            index = np.argmax(pred)

            turn = Turn.NEW_MODEL

            # pass
            if index == BOARD_SIZE:
                pass_count += 1
                continue
            # 置く
            _put(data, index, oldModelColor, newModelColor)
        else:
            self_state = [1 if d == newModelColor else 0 for row in data for d in row]
            other_state = [1 if d == oldModelColor else 0 for row in data for d in row]
            state = State(self_state, other_state)
            action = new_policy_func(new_model, state)

            turn = Turn.OLD_MODEL

            if action == BOARD_SIZE:
                pass_count += 1
                continue
            # 次の状態の取得
            state = state.next(action)
            self_state = state.enemy_pieces  # nextで入れ替わっている
            other_state = state.pieces
            for j in range(BOARD_WIDTH):
                for i in range(BOARD_WIDTH):
                    index = j * BOARD_WIDTH + i
                    if self_state[index] == 1:
                        data[j][i] = newModelColor
                    elif other_state[index] == 1:
                        data[j][i] = oldModelColor
                    else:
                        data[j][i] = 0

        if disp_log:
            _print_data(data, count)

        count += 1
        pass_count = 0

    old_model_count = sum(row.count(oldModelColor) for row in data)
    new_model_count = sum(row.count(newModelColor) for row in data)
    if disp_log:
        print(
            f"old:{old_model_count}, new:{new_model_count}, {'old model' if old_model_count > new_model_count else 'new model'} win"
        )

    return Turn.OLD_MODEL if old_model_count > new_model_count else Turn.NEW_MODEL


def _new_policy_func_mcts(model: Model, state: State):
    scores = pv_mcts_scores(new_model, state, 1)
    action = np.random.choice(state.legal_actions(), p=scores)
    return action


def _new_policy_func_pred_only(model: Model, state: State):
    policy, _ = mcts_predict(model, state)
    action = state.legal_actions()[np.argmax(policy)]
    return action


def _print_data(data: list, count: int):
    print(f"count:{count}::::::::::::::")
    for row in data:
        s = ""
        for d in row:
            if d == 0:
                s += "□"
            elif d == 1:
                s += "○"
            else:
                s += "●"
        print(s)
    print("")


def _put(data: list, index: int, selfColor: int, otherColor: int):

    y = index // BOARD_WIDTH
    x = index % BOARD_WIDTH
    data[y][x] = selfColor

    for j in range(-1, 2):
        for i in range(-1, 2):
            if _enable_reverse(data, index, selfColor, otherColor, j, i):
                _reverse(data, index, selfColor, otherColor, j, i)


def _enable_reverse(
    data: list, index: int, selfColor: int, otherColor: int, j: int, i: int
) -> bool:

    if j == 0 and i == 0:
        return False

    y = index // BOARD_WIDTH + j
    x = index % BOARD_WIDTH + i

    # 1つ隣が相手でない。置けない
    if not _enable_cell(x, y) or data[y][x] != otherColor:
        return False

    x += i
    y += j

    # 相手以外になるまでループ
    while _enable_cell(x, y) and data[y][x] == otherColor:
        x += i
        y += j

    return _enable_cell(x, y) and data[y][x] == selfColor


def _reverse(data: list, index: int, selfColor: int, otherColor: int, j: int, i: int):

    # 置けるチェック前提

    y = index // BOARD_WIDTH + j
    x = index % BOARD_WIDTH + i

    while _enable_cell(x, y) and data[y][x] == otherColor:
        data[y][x] = selfColor
        x += i
        y += j


def _enable_cell(x, y):
    return x >= 0 and y >= 0 and x < BOARD_WIDTH and y < BOARD_WIDTH


def _test_with_old_model(title, func):
    print(title)
    first_turn = True
    game_result = [0, 0]

    for _ in tqdm(range(EN_GAME_COUNT), desc="Cycle", leave=False):
        game_result[play(first_turn, func).value] += 1
        first_turn ^= True
    print(f"result: old model win:{game_result[0]}, new model win:{game_result[1]}")
    return VsOldModelResult(game_result[0], game_result[1])


def test_with_old_model(progress: Progress):
    global old_model, new_model
    load_old_model()

    """
    progress.add_vs_old_result(
        _test_with_old_model("vs old model", _new_policy_func_mcts)
    )
    """

    progress.add_vs_old_pred_only_result(
        _test_with_old_model("vs old model(pred only)", _new_policy_func_pred_only)
    )

    # モデルの破棄
    K.clear_session()
    del old_model
    del new_model


if __name__ == "__main__":
    progress = Progress()
    test_with_old_model(progress)
    progress.print()
