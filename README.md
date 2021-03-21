# xfiles-generator
Web app that uses a trained RNN model to generate new X-Files script text, which is then streamed back to the user and displayed on the screen as the model predicts each character. Written in Python using TensorFlow and Flask.

https://xfilesgenerator.com

![alt text](./screenshot.png)

## Setup
```
git clone https://github.com/susieward/files-generator
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
python3 -m flask run
```
