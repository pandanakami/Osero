import os

print("load start : path_mng")


# google colab起動か否か
def is_colab():
    # cpu起動でもCOLAB_GPUのキーはある
    return "COLAB_GPU" in os.environ


if is_colab():
    from tqdm.notebook import tqdm as tqdm
else:
    from tqdm import tqdm as tqdm


def get_path(path):
    if is_colab():
        return os.path.join("/content/drive/MyDrive/osero_rl/", path)
    else:
        return path


print("load end : path_mng")
