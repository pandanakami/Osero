import os


# google colab起動か否か
def is_colab():
    # cpu起動でもCOLAB_GPUのキーはある
    return "COLAB_GPU" in os.environ


def get_path(path):
    if is_colab():
        return os.path.join("/content/drive/MyDrive/osero_rl/", path)
    else:
        return path
