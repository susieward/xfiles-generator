import tensorflow as tf
from tensorflow.keras.models import load_model
from utils import generate_text
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
#app.secret_key = os.urandom(42)

loaded_model = load_model('./model/trained_rnn.h5')

@app.route("/submit", methods=['POST'])
def submit():
    start_string = request.json.get('start_string')
    char_length = int(request.json.get('char_length'))
    temp = float(request.json.get('temp'))
    result = generate_text(model = loaded_model, char_length = char_length, temp = temp, start_string = start_string)
    return jsonify({ 'result': result })

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(threaded=True, port=5000)
