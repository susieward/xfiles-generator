import tensorflow as tf
from tensorflow.keras.models import load_model
from utils import generate_text
from form import ReusableForm
from flask import Flask, render_template, request

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

#links = ['about']

loaded_model = load_model('./model/trained_model.h5')

#async def get_result(model, char_length, temp, start_string):
    #return await generate_text(model, char_length, temp, start_string)

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)

    if request.method == 'POST' and form.validate():
        start_string = request.form['start_string']
        temperature = float(request.form['temperature'])
        char_length = int(request.form['char_length'])

        result = generate_text(model = loaded_model, char_length = char_length, temp = temperature, start_string = start_string)

        return render_template('index.html', form = form, input = result)
    return render_template('index.html', form = form, input = None)


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
