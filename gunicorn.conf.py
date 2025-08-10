import asyncio
import multiprocessing
import sys

import uvloop
from gunicorn.arbiter import Arbiter  # type: ignore
from uvicorn_worker import UvicornWorker  # type: ignore

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
workers = 1 # TODO Deni: remove for production
worker_class = "uvicorn_worker.UvicornWorker"
accesslog = "-"
errorlog = "-"
loglevel = "info"
timeout = 60
graceful_timeout = 30

def on_starting(server: Arbiter) -> None:
    server.log.info("🚀 Starting Gunicorn with uvloop...")

def on_exit(server: Arbiter) -> None:
    server.log.info("👋 Gunicorn is shutting down...")


def worker_int(worker: UvicornWorker) -> None:
    worker.log.info("🛑 Worker received INT signal, shutting down gracefully...")
    sys.exit(0)

def worker_abort(worker: UvicornWorker) -> None:
    worker.log.warning("⚠️ Worker aborted due to timeout or unexpected error.")
