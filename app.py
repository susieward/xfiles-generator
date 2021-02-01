import tensorflow as tf
import numpy as np
from utils import load_saved_model
from flask import Flask, render_template, request, stream_with_context, Response

app = Flask(__name__)

loaded_model = load_saved_model()

path_to_file = './data/xfiles_117.txt'
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')
vocab = sorted(set(text))
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

def generate_char(model, temperature, input_eval):
    predictions = model(input_eval)
    predictions = tf.squeeze(predictions, 0)
    predictions = predictions / temperature
    predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
    char = idx2char[predicted_id]
    input_eval = tf.expand_dims([predicted_id], 0)
    return char, input_eval

@app.route('/stream', methods=['POST'])
def streamed_response():
    start_string = request.json.get('start_string')
    char_length = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))
    model = loaded_model
    def generate():
        num_generate = char_length;
        input_eval = [char2idx[s] for s in start_string]
        input_eval = tf.expand_dims(input_eval, 0)
        char = None
        model.reset_states()
        for i in range(num_generate):
            char, input_eval = generate_char(model, temperature, input_eval)
            yield char
    return Response(stream_with_context(generate()))


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
