import gc
import traceback
from typing import Dict, List
from transformers import GPT2Tokenizer
from app.models.transformer.custom_model import CustomModel

class TextGenerator:
    def __init__(self, config):
        self._config = config
        self.initialized = False
        self.model_kwargs = {
            'do_sample': True,
            'top_k': 50,
            'top_p': 1.0
        }

    async def initialize(self):
        print('spinning up generator')
        self._tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        self._model = CustomModel.from_pretrained(self._config.MODEL_PATH, low_cpu_mem_usage=True)
        self.initialized = True
        print('generator online')
        return self

    async def shutdown(self):
        print('shutting down generator')
        del self._model
        del self._tokenizer
        self.initialized = False
        gc.collect()
        print('shutdown complete. generator offline')
        return True

    async def generate_sync(self, start_string, max_length):
        outputs = self._create_generator(start_string, max_length, use_sync=True)
        generated = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated

    async def generate(self, start_string, max_length):
        generator = self._create_generator(start_string, max_length)

        async for output in generator:
            yield self._tokenizer.decode(output, skip_special_tokens=True)


    def _create_generator(self, start_string, max_length, use_sync=False):
        inputs = self._tokenizer(start_string, return_tensors="pt")

        return self._model.generate(
            max_length=max_length,
            sync=use_sync,
            **inputs,
            **self.model_kwargs
        )
