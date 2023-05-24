

class Astroquanta:
    def __init__(self, region):
        # the ID of the region to which the astroquanta belongs
        self.region = region
        # whether the region is initialized
        self.is_initialized = False
        # brief summary of the astroquanta
        self.description = ''
        # systems including a sun and (usually) some orbiting bodies
        self.solar_systems = []
        # other phenomena, be it rogue planets, star bases, giant creatures, mysterious signals, etc
        self.phenomena = []

    def generate(self):
        '''Generate the properties of this particular astroquanta using an LLM'''
        self.is_initialized = True