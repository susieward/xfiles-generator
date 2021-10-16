import traceback
from app.api.exceptions import TextGeneratorException
from typing import Dict, List

class TextGenerator:
    def __init__(self, model, tokenizer):
        self._model = model
        self._tokenizer = tokenizer

    async def generate(self, data: Dict):
        start_string = data.get('start_string')
        num_generate = int(data.get('char_length'))
        temperature = float(data.get('temp'))

        input_ids = self.preprocess_inputs(start_string)
        generator = self._model.generate(
            input_ids,
            do_sample=True,
            max_length=num_generate
        )
        for output in generator:
            result = self.postprocess_outputs(output)
            yield result

    def preprocess_inputs(self, input):
        return self._tokenizer.encode(input, return_tensors="pt")

    def postprocess_outputs(self, output):
        return self._tokenizer.decode(output, skip_special_tokens=True)

    async def _generate_text(self, input, max_length, temperature):
        try:
            input_ids = self._tokenizer.encode(input, return_tensors="pt")
            generator = self._model.generate(
                input_ids,
                do_sample=True,
                max_length=max_length
            )
            #unknowns = [126, 240, 227]

            #for output in generator:
            #    token = output.numpy().tolist()[0]
            #    if token in unknowns:
            #        if token == 126:
            #            yield "'"
            #        elif token == 227:
            #            yield ''
            #        else:
            #            continue
            #    else:
                    #text = self._tokenizer.decode(output, skip_special_tokens=True)
                    #yield text

        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

    #async def generate_chars(self, start_string, num_generate, temperature):
        #input_eval = [self.char2idx[s] for s in start_string]
        #input_eval = expand_dims(input_eval, 0)
        #self.model.reset_states()

        #for i in range(num_generate):
        #    predictions = self._model(input_eval)
            # remove the batch dimension
        #    predictions = squeeze(predictions, 0)
            # using a categorical distribution to predict the character returned by the model
        #    predictions = predictions / temperature
        #    predicted_id = random.categorical(predictions, num_samples=1)[-1,0].numpy()
            # We pass the predicted character as the next input to the model
            # along with the previous hidden state
        #    input_eval = expand_dims([predicted_id], 0)
        #    char = self.idx2char[predicted_id]
        #    yield char
