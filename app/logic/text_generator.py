from typing import Dict, List
from app.logic.generator import Generator

class TextGeneratorService:
    def __init__(self):
        self._generator = Generator()

    async def __aenter__(self):
        if not self._generator.initialized:
            print('spinning up generator')
            await self._generator.initialize()
            print('generator online')
        return self


    async def __aexit__(self, exc_type, exc_value, traceback):
        print('TextGeneratorService: exit called:', exc_type, exc_value, traceback)
        try:
            if self._generator.initialized:
                print('shutting down generator')
                await self._generator.shutdown()
                print('shutdown complete. generator offline')
        except Exception as e:
            print(e)
            pass
        finally:
            return True

    async def generate(self, data: Dict):
        start_string = data.get('start_string')
        max_length = int(data.get('char_length'))
        #temperature = float(data.get('temp'))

        gen = self._generator._generate(start_string, max_length)
        while True:
            try:
                yield await gen.__anext__()
            except StopAsyncIteration:
                break
            except Exception as exc:
                print('TextGeneratorService:', exc)
                raise exc
