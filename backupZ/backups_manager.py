

class BackupsManager:
    def __init__(self):
        self._config = None

    def set_config(self, config):
        self._config = config

    def start_watching_time(self):
        self._walk_trough_blocks()

    def _walk_trough_blocks(self):
        for main_block in self._config.blocks:
            for directive in main_block.directives:
                pass



