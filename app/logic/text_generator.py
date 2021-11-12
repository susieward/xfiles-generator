import gc
import traceback
from typing import Dict, List
from transformers import GPT2TokenizerFast
from app.models.transformer.custom_model import CustomModel
from transformers import pipeline

class TextGenerator:
    def __init__(self, config):
        self._config = config
        self.initialized = False
        self._pipeline = None
        self.model_kwargs = {
            'do_sample': True,
            'top_k': 50,
            'top_p': 1.0
        }

    async def initialize(self):
        print('spinning up generator')
        self._tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
        self._model = CustomModel.from_pretrained(self._config.MODEL_PATH, low_cpu_mem_usage=True)
        self.initialized = True
        print('generator online')
        return self

    async def shutdown(self):
        print('shutting down generator')
        del self._model
        del self._tokenizer
        if self._pipeline is not None:
            del self._pipeline
        self.initialized = False
        gc.collect()
        print('shutdown complete. generator offline')
        return True

    async def generate(self, start_string, max_length, use_pipeline=False):
        gen = self._create_generator(start_string, max_length, use_pipeline)
        try:
            if use_pipeline:
                output = self._tokenizer.decode(gen[0], skip_special_tokens=True)
                yield output
            else:
                async for output in gen:
                    yield self._tokenizer.decode(output, skip_special_tokens=True)
        except Exception as exc:
            print('TextGenerator.generate: ', exc)
            raise exc

    def _create_generator(self, start_string, max_length, use_pipeline=False):
        inputs = self._tokenizer(start_string, return_tensors="pt")
        print(inputs)

        return self._model.generate(
            max_length=max_length,
            pipeline=use_pipeline,
            **inputs,
            **self.model_kwargs
        )
