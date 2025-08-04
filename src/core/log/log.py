import logging
import sys
import uuid

import logging_loki
from fastapi import Request

from src.core.exception.exceptions import DomainException
from src.core.log.adapter.log_adapter import LoggerAdapter
from src.core.log.filter.loki_filter import LokiLevelFilter
from src.core.log.formatter.console import ConsoleFormatter
from src.core.log.formatter.loki import LokiJSONFormatter


class Log:
    def __init__(
            self,
            app_name: str,
            env: str,
            service_name: str,
            loki_url: str,
            log_level: str = "DEBUG",
            loki_enabled: bool = False,
            log_format: str = "json"
    ):
        self.app_name = app_name
        self.env = env
        self.service_name = service_name
        self.loki_url = loki_url
        self.log_level = log_level
        self.loki_enabled = loki_enabled
        self.log_format = log_format
        self.setup()

        self.base_logger = logging.getLogger(app_name)
        self.logger = LoggerAdapter(self.base_logger)

    def setup(self) -> None:
        root_logger = logging.getLogger()
        root_logger.handlers.clear()
        root_logger.setLevel(getattr(logging, self.log_level))

        handlers = []

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, self.log_level))
        console_handler.setFormatter(ConsoleFormatter())
        handlers.append(console_handler)

        if self.loki_enabled:
            try:
                loki_handler = logging_loki.LokiHandler(
                    url=f"{self.loki_url}/loki/api/v1/push",
                    tags={
                        "app": self.app_name,
                        "env": self.env,
                        "service_name": self.service_name,
                    },
                    version="1",
                )
                loki_handler.addFilter(filter=LokiLevelFilter())
                loki_handler.setLevel(getattr(logging, self.log_level))
                loki_handler.setFormatter(LokiJSONFormatter())
                handlers.append(loki_handler)
            except Exception as e:
                print(f"Warning: An error occurred while setting up Loki logging: {e}")

        app_logger = logging.getLogger(self.app_name)
        app_logger.setLevel(getattr(logging, self.log_level))
        app_logger.handlers.clear()

        for handler in handlers:
            app_logger.addHandler(handler)

        app_logger.propagate = False

    def get_context_logger(self, **context) -> LoggerAdapter:
        return LoggerAdapter(self.base_logger, context)

    def _log(self, level: str, message: str, **kwargs) -> None:
        log_method = getattr(self.logger, level.lower())
        log_method(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        self._log("CRITICAL", message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        self.logger.warning(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        self._log("DEBUG", message, **kwargs)

    def get_request_logger(self, request: Request) -> LoggerAdapter:
        request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

        context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent", "Unknown")
        }

        return LoggerAdapter(self.base_logger, context)

    def log_request_full(
            self,
            request: Request,
            status_code: int,
            body_request: str,
            body_response: str,
            duration_ms: float
    ) -> None:
        request_logger = self.get_request_logger(request)

        message = "Request completed"
        log_data = {
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length"),
            "status_code": status_code,
            "body_request": body_request,
            "body_response": body_response,
            "duration_ms": round(duration_ms, 2)
        }

        if status_code >= 500:
            request_logger.error(message, **log_data)
        elif status_code >= 400:
            request_logger.warning(message, **log_data)
        else:
            request_logger.info(message, **log_data)

    def log_request_exception(
            self,
            request: Request,
            e: BaseException,
            body_request: str,
            duration_ms: float
    ) -> None:
        request_logger = self.get_request_logger(request)
        message = "Request failed with exception"
        log_data = {
            "content_type": request.headers.get("content-type"),
            "content_length": request.headers.get("content-length"),
            "body_request": body_request,
            "exception_type": e.__class__.__name__,
            "duration_ms": round(duration_ms, 2)
        }
        if isinstance(e, DomainException):
            ex_data = e.as_dict()
            log_data = log_data | ex_data
        else:
            log_data = log_data | e.__dict__

        request_logger.error(message, **log_data)

    def log_exception(self, message: str, exc_info: bool = True, **kwargs) -> None:
        self.logger.exception(message, exc_info=exc_info, **kwargs)
