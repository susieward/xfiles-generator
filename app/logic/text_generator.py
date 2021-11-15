import gc
import traceback
from typing import Dict, List
from transformers import GPT2Tokenizer
from app.logic.custom_model import CustomModel

class TextGenerator:
    def __init__(self, config):
        self.config = config
        self.initialized = False
        self.model_kwargs = {'do_sample': True, 'top_k': 50, 'top_p': 1.0}

    async def initialize(self):
        print('spinning up generator')
        self.tokenizer = GPT2Tokenizer.from_pretrained(self.config.TOKENIZER)
        self.model = CustomModel.from_pretrained(self.config.MODEL_PATH, low_cpu_mem_usage=True)
        #self.model.eval()
        self.initialized = True
        print('generator online')
        return self

    async def shutdown(self) -> bool:
        print('shutting down generator')
        del self.model
        del self.tokenizer
        self.initialized = False
        gc.collect()
        print('shutdown complete. generator offline')
        return True

    async def generate(self, start_string: str, max_length: int):
        generator = self._create_generator(start_string, max_length)

        async for output in generator:
            yield self.tokenizer.decode(output)

    async def generate_sync(self, start_string: str, max_length: int, **kwargs) -> str:
        return_dict = kwargs.get('return_dict_in_generate', False)
        try:
            outputs = self._create_generator(start_string, max_length, use_sync=True, **kwargs)
            if return_dict:
                return outputs
            else:
                generated = self.tokenizer.decode(outputs[0])
            return generated
        except Exception as e:
            print('TextGenerator.generate_sync: ', e)
            raise e

    def _create_generator(self, start_string: str, max_length: int, use_sync=False, **kwargs):
        inputs = self.tokenizer(start_string, return_tensors="pt")

        return self.model.generate(
            max_length=max_length,
            sync=use_sync,
            use_cache=True,
            **inputs,
            **self.model_kwargs,
            **kwargs
        )
