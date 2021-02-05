from tensorflow import random, expand_dims, squeeze
from tensorflow.keras.models import load_model
import numpy as np

path_to_file = './data/xfiles_117.txt'
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
vocab = sorted(set(text))
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

def load_saved_model():
    model = load_model('./model/trained_rnn_lstm2.h5')
    return model

def generate_chars(model, start_string, num_generate, temperature):
    input_eval = [char2idx[s] for s in start_string]
    input_eval = expand_dims(input_eval, 0)

    for i in range(num_generate):
        predictions = model(input_eval)
        # remove the batch dimension
        predictions = squeeze(predictions, 0)
        # using a categorical distribution to predict the character returned by the model
        predictions = predictions / temperature
        predicted_id = random.categorical(predictions, num_samples=1)[-1,0].numpy()
        # We pass the predicted character as the next input to the model
        # along with the previous hidden state
        input_eval = expand_dims([predicted_id], 0)
        char = idx2char[predicted_id]
        yield char
