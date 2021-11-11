import gc
import asyncio
import traceback
from typing import Dict, List
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, top_k_top_p_filtering
from app.models.transformer.custom_model import CustomModel
from transformers import pipeline
import torch
from torch import nn
from app.config import get_config


class TextGenerator:
    def __init__(self, config):
        self._config = config
        self.initialized = False
        self._pipeline = None

    async def __aenter__(self):
        if not self.initialized:
            await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        print('TextGenerator: exit called:', exc_type, exc_value, traceback)
        try:
            if self.initialized:
                await self.shutdown()
        except Exception as e:
            print(e)
            pass
        finally:
            return True

    async def initialize(self):
        print('spinning up generator')
        self._tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
        self._model = CustomModel.from_pretrained(self._config.MODEL_PATH, low_cpu_mem_usage=True)
        #self._tokenizer = GPT2TokenizerFast.from_pretrained(self._config.TOKENIZER)
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

    def _preprocess_data(self, data):
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        #temperature = float(data.get('temp'))
        return start_string, max_length

    def pipeline(self, data):
        start_string, max_length = self._preprocess_data(data)

        if not self._pipeline:
            print('spinning up pipeline')
            self._pipeline = pipeline('text-generation', model=self._config.MODEL_PATH, tokenizer=self._config.TOKENIZER)

        return self._pipeline(
            start_string,
            max_length=max_length,
            do_sample=True,
            top_k=50,
            top_p=1.0
        )

    async def generate(self, data: Dict):
        gen = self._create_generator(data)
        try:
            async for output in gen:
                yield self._tokenizer.decode(output, skip_special_tokens=True)
        except Exception as exc:
            print('TextGenerator.generate: ', exc)
            raise exc

    def _create_generator(self, data):
        start_string, max_length = self._preprocess_data(data)
        inputs = self._tokenizer(start_string, return_tensors="pt")

        print(inputs)
        return self._model.generate(
            **inputs,
            do_sample=True,
            max_length=max_length,
            top_k=50,
            top_p=1.0
        )
