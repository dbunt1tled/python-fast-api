import os
import json
from datetime import datetime
from typing import Any
from urllib.parse import urljoin, urlencode

from jinja2 import Environment, FileSystemLoader, select_autoescape, Template

from src.core.exception.error_no import ErrorNo
from src.core.exception.exceptions import NotFoundException
from functools import partial


class ViewService:
    def __init__(self, template_dirs: str | list[str], app_url: str) -> None:
        self.app_url = app_url
        if isinstance(template_dirs, str):
            template_dirs = [template_dirs]

        existing_dirs = []
        for template_dir in template_dirs:
            if not os.path.exists(template_dir):
                raise NotFoundException(
                    error_no=ErrorNo.TEMPLATE_DIR_NOT_FOUND,
                    message=f"Failed to find template directory: {template_dir}",
                )

            existing_dirs.append(template_dir)

        self.env = Environment(
            loader=FileSystemLoader(existing_dirs),
            autoescape=select_autoescape(["html", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            enable_async=True,
        )

        self.env.filters.update(
            {
                "format_date": ViewService._format_date,
                "format_currency": ViewService._format_currency,
                "truncate_words": ViewService._truncate_words,
                "json_dump": json.dumps,
            }
        )

        self.env.globals.update(
            {
                "year": datetime.now().year,
                "date": datetime.now().strftime("%d.%m.%Y"),
                "app_url": app_url,
                "url": partial(ViewService._format_url, base_url=app_url),
            }
        )

        self.template_dirs = existing_dirs
        self._cache: dict[str, Template] = {}

    async def render_template(self, template_name: str, context: dict[str, Any] | None = None) -> str:
        if context is None:
            context = {}

        template = self.env.get_template(template_name)
        rendered = await template.render_async(**context)
        return rendered

    async def render_string(self, template_string: str, context: dict[str, Any] | None = None) -> str:
        if context is None:
            context = {}

        template = self.env.from_string(template_string)
        rendered = await template.render_async(**context)
        return rendered

    async def render_with_cache(self, template_name: str, context: dict[str, Any], cache_key: str | None = None) -> str:
        if cache_key and cache_key in self._cache:
            template = self._cache[cache_key]
        else:
            template = self.env.get_template(template_name)
            if cache_key:
                self._cache[cache_key] = template

        return await template.render_async(**context)

    def clear_cache(self) -> None:
        self._cache.clear()

    @staticmethod
    def _format_date(date_input: str | datetime, format_str: str = "%d.%m.%Y") -> str:
        try:
            if isinstance(date_input, str):
                if "T" in date_input:
                    date_obj = datetime.fromisoformat(date_input.replace("Z", "+00:00"))
                else:
                    date_obj = datetime.strptime(date_input, "%Y-%m-%d")
            else:
                date_obj = date_input
            return date_obj.strftime(format_str)
        except:
            return str(date_input)

    @staticmethod
    def _format_currency(amount: float, currency: str = "$") -> str:
        return f"{amount:,.2f} {currency}".replace(",", " ")

    @staticmethod
    def _truncate_words(text: str, length: int = 50) -> str:
        if not text:
            return ""
        words = text.split()
        if len(words) <= length:
            return text
        return " ".join(words[:length]) + "..."

    @staticmethod
    def _format_url(path: str, query_params: dict[str, Any] | None = None, base_url: str = "") -> str:
        url = urljoin(base_url, path)
        if query_params:
            return f"{url}?{urlencode(query_params)}"
        return url
