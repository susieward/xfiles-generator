import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np
import os

path_to_file = './data/xfiles_117.txt'

text = open(path_to_file, 'rb').read().decode(encoding='utf-8')

vocab = sorted(set(text))
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)


def loss(labels, logits):
  return tf.keras.losses.sparse_categorical_crossentropy(labels, logits, from_logits=True)

def load_saved_model():
    model = load_model('./model/trained_rnn_lstm2.h5')
    model.compile(optimizer = 'adam', loss=loss)
    return model

def generate_text_old(model, char_length, temp, start_string):
    num_generate = char_length;

    # Converting our start string to numbers (vectorizing)
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    text_generated = []
    temperature = temp

    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
        # remove the batch dimension
        predictions = tf.squeeze(predictions, 0)

        # using a categorical distribution to predict the character returned by the model
        predictions = predictions / temperature
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

        # We pass the predicted character as the next input to the model
        # along with the previous hidden state
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated.append(idx2char[predicted_id])
        #print(text_generated)
    return (start_string + ''.join(text_generated))

def generate_text(model, char_length, temp, start_string):
    num_generate = char_length;
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)

    text_generated = []
    temperature = temp
    char = None

    model.reset_states()
    for i in range(num_generate):
        char, input_eval = generate_char(model, temperature, input_eval)
        text_generated.append(char)
        print(char)
        #print(text_generated)
    return (start_string + ''.join(text_generated))

def generate(model, char_length, temperature, start_string):
    num_generate = char_length;
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
    char = None

    model.reset_states()
    for i in range(num_generate):
        char, input_eval = generate_char(model, temperature, input_eval)
        yield char
        #text_generated.append(char)
        #print(char)
        #print(text_generated)
    #return (start_string + ''.join(text_generated))

def generate_char(model, temperature, input_eval):
    predictions = model(input_eval)
    # remove the batch dimension
    predictions = tf.squeeze(predictions, 0)
    # using a categorical distribution to predict the character returned by the model
    predictions = predictions / temperature
    predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
    char = idx2char[predicted_id]
    # We pass the predicted character as the next input to the model
    # along with the previous hidden state
    input_eval = tf.expand_dims([predicted_id], 0)
    return char, input_eval
