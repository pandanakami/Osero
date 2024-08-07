import os
import shutil
import sys

os.environ["NOT_USE_MODEL"] = "True"
from progress import Progress, ProgressState
from path_mng import get_path


def reset_progress(loop_index):
    progress = Progress.load()

    progress.loop_index = loop_index
    progress.reset_play_count()
    progress.set_state(ProgressState.START)

    path = get_path("game_history_tmp.pkl")
    if os.path.exists(path):
        os.remove(path)
    print(f"do reset, index:{progress.loop_index}")


if __name__ == "__main__":

    try:
        No = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid integer.")
        sys.exit(1)

    reset_progress(No)
