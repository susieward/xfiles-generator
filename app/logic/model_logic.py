import gc
import os
import numpy
import torch
from onnxruntime.transformers.gpt2_helper import Gpt2Helper, GPT2Config
from transformers import GPT2Tokenizer
from app.config import get_config
from onnxruntime import InferenceSession
from torch import nn
from transformers.generation_logits_process import (
    LogitsProcessorList,
    MinLengthLogitsProcessor,
    TopKLogitsWarper
)

app_config = get_config()

cache_dir = os.path.join(".", "cache_models")
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

class ModelLogic:
    def __init__(self, device):
        self.device = device or torch.device("cpu")

    def initialize(self):
        self.session = self.get_session()
        self.tokenizer = self.get_tokenizer()
        self.model_config = self.get_model_config()
        self.logits_warper = self.get_logits_warper(config=self.model_config)
        self.logits_processor = self.get_logits_processor()
        self.num_attention_heads = self.model_config.n_head
        self.hidden_size = self.model_config.n_embd
        self.num_layer = self.model_config.n_layer
        return self

    def shutdown(self) -> bool:
        del self.tokenizer
        del self.session
        del self.model_config
        gc.collect()
        return True

    def get_inputs(self, prompt_text):
        encodings_dict = self.tokenizer.batch_encode_plus([prompt_text], padding=True)

        input_ids = torch.tensor(encodings_dict['input_ids'], dtype=torch.int64)
        attention_mask = torch.tensor(encodings_dict['attention_mask'], dtype=torch.float32)
        position_ids = (attention_mask.long().cumsum(-1) - 1)
        position_ids.masked_fill_(position_ids < 0, 0)

        #Empty Past State for generating first word
        empty_past = []
        batch_size = input_ids.size(0)
        sequence_length = input_ids.size(1)
        past_shape = [2, batch_size, self.num_attention_heads, 0, self.hidden_size // self.num_attention_heads]
        for i in range(self.num_layer):
            empty_past.append(torch.empty(past_shape).type(torch.float32).to(self.device))

        return input_ids, attention_mask, position_ids, empty_past

    def generate(self, input_text, num_tokens_to_produce=30):
        eos_token_id = self.tokenizer.eos_token_id

        input_ids, attention_mask, position_ids, past = self.get_inputs(input_text)
        batch_size = input_ids.size(0)
        has_eos = torch.zeros(batch_size, dtype=torch.bool)
        all_token_ids = input_ids.clone()

        for step in range(num_tokens_to_produce):
            outputs = self.inference_with_io_binding(input_ids, position_ids, attention_mask, past)

            next_token_logits = outputs[0][:, -1, :]

            # pre-process distribution
            next_token_scores = self.logits_processor(input_ids, next_token_logits)
            next_token_scores = self.logits_warper(input_ids, next_token_scores)

            # sample
            probs = nn.functional.softmax(next_token_scores, dim=-1)
            next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

            yield self.tokenizer.decode(next_tokens, skip_special_tokens=True)

            has_eos = has_eos | (next_tokens == eos_token_id)
            tokens_to_add = next_tokens.masked_fill(has_eos, eos_token_id)
            all_token_ids = torch.cat([all_token_ids, tokens_to_add.unsqueeze(-1)], dim=-1)

            # Update input_ids, attention_mask, position_ids and past
            input_ids = tokens_to_add.clone().detach().reshape([batch_size, 1]).to(self.device)
            position_ids = (position_ids[:,-1] + 1).reshape(batch_size,1)
            attention_mask = torch.cat([attention_mask, torch.ones([batch_size, 1]).type_as(attention_mask)], 1).to(self.device)

            past = []
            for i in range(self.num_layer):
                past_i = torch.from_numpy(outputs[i + 1]) if isinstance(outputs[i + 1], numpy.ndarray) else outputs[i + 1].clone().detach()
                past.append(past_i.to(self.device))

            if torch.all(has_eos):
                break

    def inference_with_io_binding(self, input_ids, position_ids, attention_mask, past):
        output_shapes = Gpt2Helper.get_output_shapes(
            batch_size=input_ids.size(0),
            past_sequence_length=past[0].size(3),
            sequence_length=input_ids.size(1),
            config=self.model_config
        )
        output_buffers = Gpt2Helper.get_output_buffers(output_shapes, self.device)

        io_binding = Gpt2Helper.prepare_io_binding(self.session, input_ids, position_ids, attention_mask, past, output_buffers, output_shapes)
        self.session.run_with_iobinding(io_binding)

        outputs = Gpt2Helper.get_outputs_from_io_binding_buffer(self.session, output_buffers, output_shapes, return_numpy=False)
        return outputs

    def get_session(self):
        onnx_model_path = app_config.ONNX_PATH
        session = InferenceSession(onnx_model_path)
        return session

    def get_tokenizer(self, app_config=app_config):
        tokenizer = GPT2Tokenizer.from_pretrained(app_config.TOKENIZER, cache_dir=cache_dir)
        tokenizer.padding_side = "left"
        tokenizer.pad_token = tokenizer.eos_token
        #tokenizer.add_special_tokens({'pad_token': '[PAD]'})
        return tokenizer

    def get_model_config(self, app_config=app_config):
        model_config = GPT2Config.from_pretrained(app_config.MODEL_PATH, cache_dir=cache_dir)
        return model_config

    def get_logits_warper(self, top_k: int = 50, top_p: float = 1.0, config = None):
        # init warp parameters
        top_k = top_k if top_k is not None else config.top_k
        top_p = top_p if top_p is not None else config.top_p
        # instantiate warpers list
        warpers = LogitsProcessorList()
        warpers.append(TopKLogitsWarper(top_k=top_k, min_tokens_to_keep=1))
        return warpers

    def get_logits_processor(self, min_length=10):
        eos_token_id = self.tokenizer.eos_token_id
        processors = LogitsProcessorList()
        processors.append(MinLengthLogitsProcessor(min_length, eos_token_id))
        return processors
