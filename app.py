import asyncio
import numpy as np
import tensorflow as tf
from utils import load_saved_model, char2idx, idx2char
from flask import Flask, render_template, request, stream_with_context, Response

app = Flask(__name__)
model = load_saved_model()

def generate_char(model, temperature, input_eval):
    predictions = model(input_eval)
    predictions = tf.squeeze(predictions, 0)
    predictions = predictions / temperature
    predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()
    char = idx2char[predicted_id]
    input_eval = tf.expand_dims([predicted_id], 0)
    return char, input_eval

async def stream_chars(request):
    start_string = request.json.get('start_string')
    num_generate = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))
    model.reset_states()

    def generate():
        input_eval = [char2idx[s] for s in start_string]
        input_eval = tf.expand_dims(input_eval, 0)
        for i in range(num_generate):
            char, input_eval = generate_char(model, temperature, input_eval)
            yield char
    return Response(stream_with_context(generate()))

@app.route('/stream', methods=['POST'])
def streamed_response():
    return asyncio.run(stream_chars(request = request))


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
