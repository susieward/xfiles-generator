import gc
import traceback
from typing import Dict, List
from transformers import GPT2Tokenizer
from app.models.transformer.custom_model import CustomModel
from app.config import get_config

class TextGenerator:
    def __init__(self):
        self.config = get_config()
        self.initialized = False

    async def initialize(self):
        self._model = CustomModel.from_pretrained(self.config.MODEL_PATH)
        self._tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        #self._model.eval()
        self.initialized = True

    async def cleanup(self):
        del self._model
        del self._tokenizer
        gc.collect()
        self.initialized = False

    async def generate(self, data: Dict):
        start_string = data.get('start_string')
        num_generate = int(data.get('char_length'))
        #temperature = float(data.get('temp'))

        input_ids = self._tokenizer.encode(start_string, return_tensors="pt")

        async for result in self._generate_text(input_ids, num_generate):
            yield result

    async def _generate_text(self, input_ids, max_length):
        try:
            generator = self._model.generate(
                input_ids,
                do_sample=True,
                max_length=max_length
            )
            for output in generator:
                text = self._tokenizer.decode(output, skip_special_tokens=True)
                yield text
        except Exception as e:
           print(e)
           traceback.print_exc()
           raise e
