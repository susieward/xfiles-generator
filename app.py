import zlib
from utils import load_saved_model, generate_chars
from flask import Flask, render_template, request, Response, stream_with_context

app = Flask(__name__)
model = load_saved_model()

@app.route('/stream', methods=['POST'])
def streamed_response():
    start_string = request.json.get('start_string')
    num_generate = int(request.json.get('char_length'))
    temperature = float(request.json.get('temp'))

    model.reset_states()
    def generate():
        buffer = []
        c = zlib.compressobj()
        gen_chars = generate_chars(model, start_string, num_generate, temperature)
        for char in gen_chars:
            buffer.append(char)
            if len(buffer) == 8:
                data = ''.join(buffer).encode('utf-8')
                chunk = c.compress(data)
                if chunk:
                    yield chunk
                buffer.clear()
                yield c.flush(zlib.Z_SYNC_FLUSH)
        yield c.flush(zlib.Z_SYNC_FLUSH)
    return Response(stream_with_context(generate()), headers = { 'Content-Encoding': 'deflate' })

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()
