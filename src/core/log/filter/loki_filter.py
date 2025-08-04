import logging

class LokiLevelFilter(logging.Filter):
    def __init__(self, levels_to_loki: list[str] | None= None):
        super().__init__()
        self.levels_to_loki = levels_to_loki or ['ERROR', 'CRITICAL']

    def filter(self, record):
        return record.levelname in self.levels_to_loki