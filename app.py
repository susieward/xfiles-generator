from utils import generate_text, load_saved_model
from form import ReusableForm
from flask import Flask, render_template, request


app = Flask(__name__)

links = ['about']

loaded_model = load_saved_model()

@app.route("/", methods=['GET', 'POST'])
def index():
    form = ReusableForm(request.form)
    if request.method == 'POST' and form.validate():

        start_string = request.form['start_string']
        temperature = float(request.form['temperature'])
        char_length = int(request.form['char_length'])

        input = generate_text(model = loaded_model, char_length = char_length, temp = temperature, start_string = start_string)
        return render_template('index.html', links = links, form = form, input = input)
    return render_template('index.html', links = links, form = form, input = None)

if __name__ == '__main__':
    app.run(debug = True)
