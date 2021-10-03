import numpy as np
from typing import Callable
from fastapi import FastAPI


def init_char_lookup(app: FastAPI) -> Callable:
    def _get_char_lookup():
        path_to_file = './app/model/data/xfiles_117.txt'
        with open(path_to_file, 'rb') as f:
            text = f.read().decode(encoding='utf-8')

        vocab = sorted(set(text))
        app.state.char2idx = {u:i for i, u in enumerate(vocab)}
        app.state.idx2char = np.array(vocab)

    return _get_char_lookup
