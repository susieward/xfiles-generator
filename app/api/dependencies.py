from fastapi import Request, Depends, WebSocket
from tensorflow.keras.models import load_model
from app.model.custom_training import CustomTraining
from app.logic.text_generator import TextGenerator

path = './app/model/rnn/trained_rnn_lstm5.h5'

def get_model():
    model = load_model(path, custom_objects={'CustomTraining': CustomTraining})
    return model

def get_char2idx(request: WebSocket):
    return request.app.state.char2idx

def get_idx2char(request: WebSocket):
    return request.app.state.idx2char

def text_generator_dependency(
    model = Depends(get_model),
    char2idx = Depends(get_char2idx),
    idx2char = Depends(get_idx2char)
) -> TextGenerator:
    return TextGenerator(model=model, char2idx=char2idx, idx2char=idx2char)
