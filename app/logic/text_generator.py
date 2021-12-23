from app.logic.model_logic import ModelLogic

class TextGenerator:
    def __init__(self, config, device=None):
        self.model = ModelLogic(device=device)
        self.config = config
        self.initialized = False

    async def initialize(self):
        print('spinning up generator')
        self.model.initialize()
        self.initialized = True
        print('generator online')
        return self

    async def shutdown(self) -> bool:
        print('shutting down generator')
        self.model.shutdown()
        self.initialized = False
        print('shutdown complete. generator offline')
        return True

    async def generate(self, start_string: str, max_length: int):
        try:
            for output in self.model.generate(start_string, max_length):
                yield output
        except Exception as e:
            print('generate:', e)
            raise e
