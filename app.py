import asyncio
import threading
from utils import generate_text, load_saved_model
from form import ReusableForm
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#links = ['about']

loaded_model = load_saved_model()

async def get_result(model, char_length, temp, start_string):
    return await generate_text(model, char_length, temp, start_string)

@app.route("/result", methods=['GET', 'POST'])
def result():
    form = ReusableForm(request.form)

    if request.method == 'GET':
        start_string = request.args.get('start_string')
        temperature = float(request.args.get('temperature'))
        char_length = int(request.args.get('char_length'))
    else:
        start_string = request.form['start_string']
        temperature = float(request.form['temperature'])
        char_length = int(request.form['char_length'])

    result = asyncio.run(get_result(model = loaded_model, char_length = char_length, temp = temperature, start_string = start_string))

    return render_template('index.html', form = form, input = result)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)

    if request.method == 'POST' and form.validate():
        start_string = request.form['start_string']
        temperature = float(request.form['temperature'])
        char_length = int(request.form['char_length'])

        return redirect(url_for('result', start_string = start_string, temperature = temperature, char_length = char_length))
    return render_template('index.html', form = form, input = None)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
