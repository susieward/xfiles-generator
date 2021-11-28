import gc
from app.logic.model_logic import _generate, get_tokenizer, get_session

class TextGenerator:
    def __init__(self, config):
        self.config = config
        self.initialized = False

    async def initialize(self):
        print('spinning up generator')
        self.session = get_session()
        self.tokenizer = get_tokenizer()
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
        generator = _generate(self.tokenizer, start_string, self.session, max_length)

        for output in generator:
            yield output
