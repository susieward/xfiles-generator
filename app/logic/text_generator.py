import gc
import traceback
from typing import Dict, List
#from transformers import GPT2Tokenizer
#from app.logic.custom_model import CustomModel
from app.logic.model_logic import _generate, get_tokenizer
import onnxruntime

class TextGenerator:
    def __init__(self, config):
        self.config = config
        self.initialized = False

    async def initialize(self):
        print('spinning up generator')
        self.session = onnxruntime.InferenceSession(self.config.ONNX_PATH)
        self.tokenizer = get_tokenizer()
        #self.tokenizer = GPT2Tokenizer.from_pretrained(self.config.TOKENIZER)
        #model = CustomModel.from_pretrained(self.config.MODEL_PATH, low_cpu_mem_usage=True)
        #device = torch.device("cpu")
        #model.eval().to(device)
        #self.model = model
        self.initialized = True
        print('generator online')
        return self

    async def shutdown(self) -> bool:
        print('shutting down generator')
        #del self.model
        del self.tokenizer
        del self.session
        self.initialized = False
        gc.collect()
        print('shutdown complete. generator offline')
        return True

    async def generate(self, start_string: str, max_length: int):
        #generator = self._create_generator(start_string, max_length)
        generator = _generate(self.tokenizer, start_string, self.session, max_length)

        for output in generator:
            yield output
            #yield self._decode(output)

    def generate_sync(self, start_string: str, max_length: int, **kwargs):
        return_dict = kwargs.get('return_dict_in_generate', False)
        try:
            outputs = self._create_generator(start_string, max_length, use_sync=True, **kwargs)
            if return_dict:
                return outputs

            generated = self._decode(outputs[0])
            return generated
        except Exception as e:
            print('TextGenerator.generate_sync: ', e)
            raise e

    def _decode(self, sequence):
        return self.tokenizer.decode(
            sequence,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True
        )

    def _create_generator(self, start_string: str, max_length: int, use_sync=False, **kwargs):
        inputs = self.tokenizer(start_string, padding=False, add_special_tokens=False, return_tensors="pt")
        input_ids = inputs['input_ids']

        return self.model.generate(
            input_ids=input_ids,
            max_length=max_length,
            sync=use_sync,
            do_sample=True,
            use_cache=True,
            top_k=50,
            top_p=1.0,
            **kwargs
        )
