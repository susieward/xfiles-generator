
class Config:
    RNN_PATH = './app/models/rnn/trained_rnn_lstm5.h5'
    MODEL_PATH = './app/models/transformer'
    TOKENIZER = './app/models/transformer/xfiles_tokenizer'
    TEXT_PATH = './app/models/data/xfiles_117.txt'
    LOGGING = False
    ONNX_PATH = "./onnx/generator.onnx"

def get_config():
    return Config()
