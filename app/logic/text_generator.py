import gc
import traceback
from typing import Dict, List
from transformers import GPT2Tokenizer
from app.logic.custom_model import CustomModel
import torch

class TextGenerator:
    def __init__(self, config):
        self.config = config
        self.initialized = False

    async def initialize(self):
        print('spinning up generator')
        self.tokenizer = GPT2Tokenizer.from_pretrained('gpt2')
        model = CustomModel.from_pretrained(self.config.MODEL_PATH, low_cpu_mem_usage=True, torch_dtype=torch.float32)
        model.eval()
        self.model = model
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
            yield self.tokenizer.decode(output, skip_special_tokens=True)

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
        input_ids = inputs['input_ids']

        return self.model.generate(
            input_ids,
            max_length=max_length,
            sync=use_sync,
            do_sample=True,
            top_k=50,
            top_p=1.0,
            **kwargs
        )
