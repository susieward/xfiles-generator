from generator import TextGenerator
from flask import Flask, render_template, request, Response, stream_with_context
from flask_compress import Compress

app = Flask(__name__)
app.config["COMPRESS_REGISTER"] = False
compress = Compress()
compress.init_app(app)

generator = TextGenerator()

@app.route('/stream', methods=['POST'])
def streamed_response():
    start_string = request.json.get('start_string')
    num_generate = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))
    return Response(stream_with_context(generator.generate(start_string, num_generate, temperature)), headers = { 'Content-Encoding': 'deflate', 'X-Accel-Buffering': 'no' })

@app.route("/", methods=['GET'])
@compress.compressed()
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
