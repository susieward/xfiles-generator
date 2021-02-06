import zlib
from utils import load_saved_model, generate_chars
from flask import Flask, render_template, request, Response, stream_with_context
from flask_compress import Compress

app = Flask(__name__)
app.config["COMPRESS_REGISTER"] = False
compress = Compress()
compress.init_app(app)

model = load_saved_model()

@app.route('/stream', methods=['POST'])
def streamed_response():
    start_string = request.json.get('start_string')
    num_generate = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))
    model.reset_states()

    def generate():
        c = zlib.compressobj(-1, zlib.DEFLATED, -9)
        buffer = []
        gen_chars = generate_chars(model, start_string, num_generate, temperature)
        for char in gen_chars:
            data = c.compress(char.encode())
            buffer.append(data)
            if len(buffer) == 8:
                chunk = c.compress(b''.join(buffer)) + c.flush(zlib.Z_SYNC_FLUSH)
                yield chunk
                buffer.clear()
        yield c.flush(zlib.Z_SYNC_FLUSH)
    return Response(stream_with_context(generate()), headers = { 'Content-Encoding': 'deflate' })

@app.route("/", methods=['GET'])
@compress.compressed()
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
