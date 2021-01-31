# xfiles-generator
Web app that uses a character-based RNN model to generate and display new X-Files script text. Written in Python using TensorFlow and Flask.

https://xfiles-generator.herokuapp.com

![alt text](./screenshot.png)

### Note:
Due to the limited memory resources available on Heroku's free tier, the app runs much more slowly in production. To really test it out, install and run it locally.

## Setup
1. git clone
2. python3 -m venv env
3. source env/bin/activate
4. pip install -r requirements.txt
5. python3 -m flask run
6. Go to http://127.0.0.1:5000
