import os
import asyncio
import tensorflow as tf
from tensorflow.keras.models import load_model
from utils import generate_text, load_saved_model
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
app.secret_key = os.urandom(42)

loaded_model = load_saved_model()

async def get_result(char_length, temp, start_string):
    model = loaded_model
    task = asyncio.create_task(generate_text(model, char_length, temp, start_string))
    return await task

@app.route("/submit", methods=['POST'])
def submit():
    if(request.method == 'POST'):
        start_string = request.json.get('start_string')
        char_length = int(request.json.get('char_length'))
        temp = float(request.json.get('temp'))
        result = asyncio.run(get_result(char_length, temp, start_string))
        return jsonify({ 'result': result })


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
