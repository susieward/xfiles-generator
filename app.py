import tensorflow as tf
from utils import load_saved_model, generate_char, char2idx
from flask import Flask, render_template, request, Response

app = Flask(__name__)

model = load_saved_model()

def generate_chars(temperature, num_generate, start_string):
    input_eval = [char2idx[s] for s in start_string]
    input_eval = tf.expand_dims(input_eval, 0)
    for i in range(num_generate):
        char, input_eval = generate_char(model, temperature, input_eval)
        yield char

@app.route('/stream', methods=['POST'])
def streamed_response():
    start_string = request.json.get('start_string')
    num_generate = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))
    model.reset_states()
    def generate():
        for char in generate_chars(temperature, num_generate, start_string):
            yield char
    return Response(generate(), mimetype = 'text/plain')

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
