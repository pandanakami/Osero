from my_module.model import model_cmn

#####################################################
# モデル切り替え
from my_module.model import Simple_08 as m

#####################################################

MODEL_NAME = m.MODEL_NAME.split(".")[-1]

INPUT_CHANNEL = model_cmn.INPUT_CHANNEL
OSERO_HEIGHT = model_cmn.OSERO_HEIGHT
OSERO_WIDTH = model_cmn.OSERO_WIDTH
INPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH
OUTPUT_SIZE = OSERO_HEIGHT * OSERO_WIDTH + 1


def is_channel_first():
    return model_cmn.is_channel_first()


def input_shape():
    return model_cmn.input_shape()


def get_model(DEBUG=False):
    return m.get_model(DEBUG)
