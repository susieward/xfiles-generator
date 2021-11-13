# "sample" method defined below was modified from original in GenerationMixin class:
# (https://huggingface.co/transformers/_modules/transformers/generation_utils.html)
# Source code copyright 2020 The Google AI Language Team Authors, Facebook AI Research
# authors and The HuggingFace Inc. team.
# Copyright (c) 2020, NVIDIA CORPORATION.  All rights reserved.

import gc
from transformers import GPT2LMHeadModel
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Union

import torch
import torch.distributed as dist
from torch import nn

from transformers.generation_logits_process import LogitsProcessorList
from transformers.generation_stopping_criteria import (
    StoppingCriteriaList,
    validate_stopping_criteria
)

class CustomModel(GPT2LMHeadModel):
    def sample(self, *args, **kwargs):
        sync = kwargs.pop('sync', False)
        if sync:
            return super().sample(*args, **kwargs)
        else:
            return self.sample_async(*args, **kwargs)

    async def sample_async(self,
        input_ids: torch.LongTensor,
        logits_processor: Optional[LogitsProcessorList] = None,
        stopping_criteria: Optional[StoppingCriteriaList] = None,
        logits_warper: Optional[LogitsProcessorList] = None,
        max_length: Optional[int] = None,
        pad_token_id: Optional[int] = None,
        eos_token_id: Optional[int] = None,
        output_attentions: Optional[bool] = None,
        output_hidden_states: Optional[bool] = None,
        output_scores: Optional[bool] = None,
        return_dict_in_generate: Optional[bool] = None,
        synced_gpus: Optional[bool] = None,
        **model_kwargs,
    ):
        # init values
        logits_processor = logits_processor if logits_processor is not None else LogitsProcessorList()
        stopping_criteria = stopping_criteria if stopping_criteria is not None else StoppingCriteriaList()
        if max_length is not None:
            #warnings.warn(
            #    "`max_length` is deprecated in this function, use `stopping_criteria=StoppingCriteriaList(MaxLengthCriteria(max_length=max_length))` instead.",
            #    UserWarning,
            #)
            stopping_criteria = validate_stopping_criteria(stopping_criteria, max_length)
        logits_warper = logits_warper if logits_warper is not None else LogitsProcessorList()
        pad_token_id = pad_token_id if pad_token_id is not None else self.config.pad_token_id
        eos_token_id = eos_token_id if eos_token_id is not None else self.config.eos_token_id
        output_scores = output_scores if output_scores is not None else self.config.output_scores
        output_attentions = output_attentions if output_attentions is not None else self.config.output_attentions
        output_hidden_states = (
            output_hidden_states if output_hidden_states is not None else self.config.output_hidden_states
        )
        return_dict_in_generate = (
            return_dict_in_generate if return_dict_in_generate is not None else self.config.return_dict_in_generate
        )

        # init attention / hidden states / scores tuples
        scores = () if (return_dict_in_generate and output_scores) else None
        decoder_attentions = () if (return_dict_in_generate and output_attentions) else None
        cross_attentions = () if (return_dict_in_generate and output_attentions) else None
        decoder_hidden_states = () if (return_dict_in_generate and output_hidden_states) else None

        # if model is an encoder-decoder, retrieve encoder attention weights and hidden states
        if return_dict_in_generate and self.config.is_encoder_decoder:
           encoder_attentions = model_kwargs["encoder_outputs"].get("attentions") if output_attentions else None
           encoder_hidden_states = (
                model_kwargs["encoder_outputs"].get("hidden_states") if output_hidden_states else None
            )

        # keep track of which sequences are already finished
        unfinished_sequences = input_ids.new(input_ids.shape[0]).fill_(1)
        cur_len = input_ids.shape[-1]

        print(self.config.is_encoder_decoder)

        # auto-regressive generation
        print('beginning while loop...')
        while True:
            try:
                # prepare model inputs
                model_inputs = self.prepare_inputs_for_generation(input_ids, **model_kwargs)

                # forward pass to get next token
                outputs = self(
                    **model_inputs,
                    return_dict=True,
                    output_attentions=output_attentions,
                    output_hidden_states=output_hidden_states,
                )

                # get next token logits
                next_token_logits = outputs.logits[:, -1, :]

                # pre-process distribution
                next_token_scores = logits_processor(input_ids, next_token_logits)
                next_token_scores = logits_warper(input_ids, next_token_scores)

                # sample
                probs = nn.functional.softmax(next_token_scores, dim=-1)
                next_tokens = torch.multinomial(probs, num_samples=1).squeeze(1)

                del probs
                del next_token_scores
                del next_token_logits

                # finished sentences should have their next token be a padding token
                if eos_token_id is not None:
                    next_tokens = next_tokens * unfinished_sequences + pad_token_id * (1 - unfinished_sequences)

                # update generated ids, model inputs, and length for next step
                input_ids = torch.cat([input_ids, next_tokens[:, None]], dim=-1)
                model_kwargs = self._update_model_kwargs_for_generation(
                    outputs, model_kwargs, is_encoder_decoder=self.config.is_encoder_decoder
                )
                cur_len = cur_len + 1

                # if eos_token was found in one sentence, set sentence to finished
                if eos_token_id is not None:
                    unfinished_sequences = unfinished_sequences.mul((next_tokens != eos_token_id).long())

                del model_inputs
                del outputs

                yield next_tokens

                # stop when each sentence is finished, or if we exceed the maximum length
                if unfinished_sequences.max() == 0 or stopping_criteria(input_ids, scores):
                    print('time to stop')
                    del unfinished_sequences
                    gc.collect()
                    break
            except Exception as e:
                print('CustomModel.sample:', e)
                gc.collect()
                raise e
