import os

os.environ["NOT_USE_MODEL"] = "True"
from progress import Progress, ProgressState
import pickle
import os
import numpy as np


def _print_state(title: str, array: np.array):
    print(title)
    for j in range(8):
        s = ""
        for i in range(8):
            s += f"{array[j][i]}, "
        print(s)


def _get_rot90(history: list, k=0) -> list:
    new_history = []
    for h in history:
        h = history[0]
        (state, probs, value) = h
        self_state = np.array(state[0]).reshape(8, 8)
        other_state = np.array(state[1]).reshape(8, 8)
        prob = np.array(probs[:64]).reshape(8, 8)  # pass(65)抜き

        # 回転
        new_self_state = np.rot90(self_state, k=-1 * k)
        new_other_state = np.rot90(other_state, k=-1 * k)
        new_prob = np.rot90(prob, k=-1 * k)

        new_self_state = new_self_state.reshape(64).tolist()
        new_other_state = new_other_state.reshape(64).tolist()
        new_prob = new_prob.reshape(64).tolist()
        new_prob.append(probs[64])  # pass(65)戻す

        new_history.append(([new_self_state, new_other_state], new_prob, value))
    return new_history


def extend(input_dir, output_dir):

    os.makedirs(output_dir, exist_ok=True)

    PROGRESS_1_PATH = os.path.join(os.path.join(input_dir, "progress"), "progress.pkl")
    PROGRESS_OUTPUT_PATH = os.path.join(
        os.path.join(output_dir, "progress"), "progress.pkl"
    )

    HISTORY_1_PATH = os.path.join(input_dir, "game_history_tmp.pkl")
    HISTORY_OUTPUT_PATH = os.path.join(output_dir, "game_history_tmp.pkl")

    progress = Progress.load(PROGRESS_1_PATH)

    with open(HISTORY_1_PATH, "rb") as f:
        history: list = pickle.load(f)

    rot90 = _get_rot90(history, 1)
    rot180 = _get_rot90(history, 2)
    rot270 = _get_rot90(history, 3)

    history.extend(rot90)
    history.extend(rot180)
    history.extend(rot270)

    with open(HISTORY_OUTPUT_PATH, "wb") as f:
        pickle.dump(history, f)

    progress.play_count *= 4
    progress._save(PROGRESS_OUTPUT_PATH)

    print(f"extend count:{progress.play_count}, history num:{len(history)}")


if __name__ == "__main__":
    INPUT_1_DIR = "combine2"
    OUTPUT_DIR = "extend"
    extend(INPUT_1_DIR, OUTPUT_DIR)
