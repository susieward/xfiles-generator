from tensorflow import random, expand_dims, squeeze
from app.api.exceptions import TextGeneratorException

class TextGenerator:
    def __init__(self, model, char2idx, idx2char):
        self._model = model
        self.char2idx = char2idx
        self.idx2char = idx2char

    async def generate(self, data):
        start_string = data.get('start_string')
        num_generate = int(data.get('char_length'))
        temperature = float(data.get('temp'))

        async for char in self.generate_chars(start_string, num_generate, temperature):
            yield char

    async def generate_chars(self, start_string, num_generate, temperature):
        input_eval = [self.char2idx[s] for s in start_string]
        input_eval = expand_dims(input_eval, 0)
        #self.model.reset_states()

        for i in range(num_generate):
            predictions = self._model(input_eval)
            # remove the batch dimension
            predictions = squeeze(predictions, 0)
            # using a categorical distribution to predict the character returned by the model
            predictions = predictions / temperature
            predicted_id = random.categorical(predictions, num_samples=1)[-1,0].numpy()
            # We pass the predicted character as the next input to the model
            # along with the previous hidden state
            input_eval = expand_dims([predicted_id], 0)
            char = self.idx2char[predicted_id]
            yield char
