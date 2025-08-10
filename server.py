import sys
from pathlib import Path
from typing import Any

from gunicorn.app.base import BaseApplication  # type: ignore

from src.api import app

sys.path.append(str(Path(__file__).parent))

class StandaloneApplication(BaseApplication):
    def __init__(self, application: BaseApplication, option: dict[str, Any] | None=None) -> None:
        self.options = option or {}
        self.application = application
        super().__init__()

    def load_config(self) -> None:
        config = {
            key: value
            for key, value in self.options.items()
            if key in self.cfg.settings and value is not None
        }
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> BaseApplication:
        return self.application

if __name__ == "__main__":
    options = {
        "bind": "0.0.0.0:8000",
        "workers": 1, # multiprocessing.cpu_count() * 2 + 1,
        "worker_class": "uvicorn.workers.UvicornWorker",
    }
    StandaloneApplication(application=app, option=options).run()
