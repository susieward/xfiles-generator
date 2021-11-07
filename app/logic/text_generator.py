import gc
import asyncio
import traceback
from typing import Dict, List
from transformers import GPT2TokenizerFast
from app.models.transformer.custom_model import CustomModel
from transformers import pipeline
from app.config import get_config


class TextGenerator:
    def __init__(self):
        self._config = get_config()
        self.initialized = False

    async def __aenter__(self):
        if not self.initialized:
            print('spinning up generator')
            await self.initialize()
            print('generator online')
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print('TextGenerator: exit called:', exc_type, exc_value, traceback)
        try:
            if self.initialized:
                print('shutting down generator')
                await self.shutdown()
                print('shutdown complete. generator offline')
        except Exception as e:
            print(e)
            pass
        finally:
            return True

    async def initialize(self):
        #self._model = self._init_model()
        #self._tokenizer = self._init_tokenizer()
        self._pipeline = pipeline('text-generation', model=self._config.MODEL_PATH, tokenizer=self._config.TOKENIZER)
        self.initialized = True
        return self

    async def shutdown(self):
        #del self._model
        #del self._tokenizer
        del self._pipeline
        self.initialized = False
        gc.collect()
        return True

    def pipeline(self, data):
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        #inputs = self._tokenizer(start_string, return_tensors="pt")['input_ids']
        return self._pipeline(start_string, max_length=max_length, do_sample=True)

    def _init_model(self):
        model = CustomModel.from_pretrained(self._config.MODEL_PATH, low_cpu_mem_usage=True)
        return model

    def _init_tokenizer(self):
        tokenizer = GPT2TokenizerFast.from_pretrained(self._config.TOKENIZER)
        return tokenizer

    async def generate(self, data: Dict):
        gen = self._create_generator(data)
        try:
            async for output in gen:
                yield await self._decode(output)
        except Exception as exc:
            print('TextGenerator.generate: ', exc)
            raise exc

    def _create_generator(self, data):
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        #temperature = float(data.get('temp'))

        input_dict = self._tokenizer(start_string, return_tensors="pt")
        #print(input_dict)
        return self._model.generate(
            **input_dict,
            do_sample=True,
            max_length=max_length
        )

    async def _decode(self, output):
        return self._tokenizer.decode(output, skip_special_tokens=True)
