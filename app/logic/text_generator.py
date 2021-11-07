import gc
import asyncio
import traceback
from typing import Dict, List
from transformers import GPT2TokenizerFast
from app.models.transformer.custom_model import CustomModel
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
        await asyncio.gather(self._init_model(), self._init_tokenizer())
        self.initialized = True
        return self

    async def shutdown(self):
        del self._model
        del self._tokenizer
        self.initialized = False
        gc.collect()
        return True

    async def _init_model(self):
        self._model = CustomModel.from_pretrained(
            self._config.MODEL_PATH,
            low_cpu_mem_usage=True,
            local_files_only=True)
        return self

    async def _init_tokenizer(self):
        self._tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
        return self

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
            max_length=max_length,
            use_cache=True
        )

    async def _decode(self, output):
        return self._tokenizer.decode(output, skip_special_tokens=True)
