import my_module.osero_model as osero_model
from my_module.param import OUTPUT_FILE_NAME
import keras
import os


def get_model_name() -> str:
    return OUTPUT_FILE_NAME


def load_model() -> keras.models.Sequential:
    return osero_model.load_model(OUTPUT_FILE_NAME)


def load_model_proto() -> keras.models.Sequential:
    dirname = os.path.dirname(OUTPUT_FILE_NAME)
    filename = os.path.basename(OUTPUT_FILE_NAME)
    filename_detail = os.path.splitext(OUTPUT_FILE_NAME)
    filename = filename_detail[0] + "proto" + filename_detail[1]

    return osero_model.load_model(filename)
