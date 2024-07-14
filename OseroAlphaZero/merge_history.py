import os

os.environ["NOT_USE_MODEL"] = "True"
from progress import Progress, ProgressState
import pickle
import os


def merge(input1_dir, input2_dir, output_dir):

    PROGRESS_1_PATH = os.path.join(os.path.join(input1_dir, "progress"), "progress.pkl")
    PROGRESS_2_PATH = os.path.join(os.path.join(input2_dir, "progress"), "progress.pkl")
    PROGRESS_OUTPUT_PATH = os.path.join(
        os.path.join(output_dir, "progress"), "progress.pkl"
    )

    HISTORY_1_PATH = os.path.join(input1_dir, "game_history_tmp.pkl")
    HISTORY_2_PATH = os.path.join(input2_dir, "game_history_tmp.pkl")
    HISTORY_OUTPUT_PATH = os.path.join(output_dir, "game_history_tmp.pkl")

    progress1 = Progress.load(PROGRESS_1_PATH)
    progress2 = Progress.load(PROGRESS_2_PATH)

    with open(HISTORY_1_PATH, "rb") as f:
        history1 = pickle.load(f)

    with open(HISTORY_2_PATH, "rb") as f:
        history2 = pickle.load(f)

    # 同条件であれば結合
    if (
        progress1.loop_index == progress2.loop_index
        and progress1._state == ProgressState.START
        and progress2._state == ProgressState.START
    ):
        progress1.play_count += progress2.play_count
        history: list = history1
        history.extend(history2)

        os.makedirs(output_dir, exist_ok=True)
        progress1._save(PROGRESS_OUTPUT_PATH)
        with open(HISTORY_OUTPUT_PATH, "wb") as f:
            pickle.dump(history, f)

        return True
    else:
        return False


if __name__ == "__main__":
    INPUT_1_DIR = "input3"
    INPUT_2_DIR = "combine"
    OUTPUT_DIR = "combine2"
    if merge(INPUT_1_DIR, INPUT_2_DIR, OUTPUT_DIR):
        print("Conbine!!!!")
    else:
        print("None")
