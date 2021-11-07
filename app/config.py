
class Config:
    RNN_PATH = './app/models/rnn/trained_rnn_lstm5.h5'
    MODEL_PATH = './app/models/transformer'
    TEXT_PATH = './app/models/data/xfiles_117.txt'
    LOGGING = False

def get_config():
    return Config()
