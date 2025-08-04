import logging


class LoggerAdapter(logging.LoggerAdapter):
    def __init__(self, logger, extra=None):
        super().__init__(logger, extra or {})

    def process(self, msg, kwargs):
        extra_data = self.extra.copy()
        log_kwargs = {}
        for key, value in kwargs.items():
            if key not in ["exc_info", "stack_info", "stacklevel", "extra"]:
                extra_data[key] = value
            else:
                log_kwargs[key] = value
        if "extra" not in log_kwargs:
            log_kwargs["extra"] = {}
        log_kwargs["extra"]["extra_data"] = extra_data

        return msg, log_kwargs
