import sys
import asyncio
from app.logic.text_generator import TextGenerator
from app.config import get_config


async def main(input_str, max_length, **kwargs):
    generator = TextGenerator(config=get_config())
    await generator.initialize()

    #to_decode = [1680,  314, 1265, 1997, 2073,   30,  198,  198]
    #result = self.tokenizer.decode(to_decode)
    #print('result', result)

    try:
        outputs = await generator.generate_sync(input_str, max_length, **kwargs)
        print('outputs', outputs)

        input_ids = generator.tokenizer(input_str, return_tensors="pt").input_ids
        print('input_ids:', input_ids[0])

        gen_ids = outputs["sequences"][0, input_ids.shape[-1]:]
        print('gen_ids', gen_ids)

        decoded_gen_ids = generator.tokenizer.decode(gen_ids)
        print('decoded_gen_ids', decoded_gen_ids)

        vocab_size = outputs["scores"][0].shape[-1]
        print('vocab_size', vocab_size)

        sequences = outputs['sequences'][0]
        print('sequences', sequences)
        generated = generator.tokenizer.decode(sequences, skip_special_tokens=True)

        print('generated: ', generated)
    except Exception as e:
        print(e)
    finally:
        await generator.shutdown()


if __name__ == '__main__':
    num_args = len(sys.argv) - 1
    max_length = 50
    input_str = 'SCULLY:'
    output_attn = False

    if num_args > 0:
        max_length = int(sys.argv[1])

        if num_args > 1:
            input_str = sys.argv[2]

            if num_args > 2:
                output_attn = bool(sys.argv[3])

    asyncio.run(main(input_str, max_length, return_dict_in_generate=True, output_scores=True, output_attentions=output_attn))
