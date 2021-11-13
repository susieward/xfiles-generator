import sys
import asyncio
from app.logic.text_generator import TextGenerator
from app.config import get_config


async def main(input_str, max_length, **kwargs):
    generator = TextGenerator(config=get_config())
    await generator.initialize()

    generator.model.eval()

    try:
        text = await generator.generate_sync(input_str, max_length, **kwargs)
        print('generated: ', text)
    except Exception as e:
        print(e)
    finally:
        await generator.shutdown()


if __name__ == '__main__':
    num_args = len(sys.argv) - 1
    max_length = 50
    input_str = 'SCULLY:'

    if num_args > 0:
        max_length = int(sys.argv[1])

        if num_args > 1:
            input_str = sys.argv[2]

    asyncio.run(main(input_str, max_length, return_dict_in_generate=True, output_scores=True))
