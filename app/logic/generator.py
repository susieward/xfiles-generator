import gc
import asyncio
import traceback
from transformers import GPT2TokenizerFast
from app.models.transformer.custom_model import CustomModel
from app.config import get_config

class Generator:
    def __init__(self, config = get_config()):
        self._config = config
        self.initialized = False

    async def initialize(self):
        await asyncio.gather(self._get_model(), self._get_tokenizer())
        self.initialized = True
        return self

    async def shutdown(self):
        del self._model
        del self._tokenizer
        gc.collect()
        self.initialized = False
        return True

    async def _generate(self, *args):
        try:
            async for output in self._create_generator(*args):
                yield await self._decode(output)
        except Exception as e:
            raise e

    def _create_generator(self, input, max_length):
        input_dict = self._encode(input)
        print(input_dict)
        generator = self._model.generate(
            **input_dict,
            do_sample=True,
            max_length=max_length,
            use_cache=True
        )
        return generator

    def _encode(self, input):
        return self._tokenizer(input, return_tensors="pt")

    async def _decode(self, output):
        try:
            result = self._tokenizer.decode(output, skip_special_tokens=True)
            return result
        except Exception as e:
            print('_decode', e)
            raise e

    async def _get_model(self):
        self._model = CustomModel.from_pretrained(self._config.MODEL_PATH, low_cpu_mem_usage=True)
        return self

    async def _get_tokenizer(self):
        self._tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
        return self
