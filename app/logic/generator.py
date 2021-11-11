import gc
import asyncio
import traceback
from transformers import GPT2LMHeadModel, GPT2TokenizerFast, top_k_top_p_filtering
from app.models.transformer.custom_model import CustomModel
from app.config import get_config
import torch
from torch import nn



async def get_generated(sequence, max_length, tokenizer, model):
    config = get_config()
    tokenizer = GPT2TokenizerFast.from_pretrained('gpt2')
    model = GPT2LMHeadModel.from_pretrained(config.MODEL_PATH, low_cpu_mem_usage=True)

    inputs = tokenizer(sequence, return_tensors="pt")
    sequences = []

    input_ids = inputs["input_ids"]

    while True:
        try:
            generated = generate(input_ids, **inputs)
            encoded = generated.tolist()[0]
            decoded_seq = tokenizer.decode(encoded)
            sequences.append(decoded_seq)

            if len(sequences) == max_length:
                text = ''.join(sequences)
                print(text)
                break
            input_ids = encoded

        except Exception as e:
            print(e)
            raise e




def generate(input_ids, **inputs):
    #input_ids = inputs["input_ids"]

    # get logits of last hidden state
    next_token_logits = model(input_ids=input_ids, **inputs).logits[:, -1, :]

    # filter
    filtered_next_token_logits = top_k_top_p_filtering(next_token_logits, top_k=50, top_p=1.0)

    # sample
    probs = nn.functional.softmax(filtered_next_token_logits, dim=-1)
    next_token = torch.multinomial(probs, num_samples=1)
    generated = torch.cat([input_ids, next_token], dim=-1)

    yield generated

    #resulting_string = tokenizer.decode(generated.tolist()[0])
    #print(resulting_string)
    #return resulting_string


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
