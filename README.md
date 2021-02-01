# xfiles-generator
Web app that uses a trained RNN model to generate new X-Files script text, which is then streamed back to the user and displayed on the screen as the model predicts each character. Written in Python using TensorFlow and Flask.

https://xfiles-generator.herokuapp.com

![alt text](./screenshot.png)

## Setup
1. git clone
2. python3 -m venv env
3. source env/bin/activate
4. pip install -r requirements.txt
5. python3 -m flask run
6. Go to http://127.0.0.1:5000
