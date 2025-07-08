from fastapi import FastAPI
from typing import List, Type

from src.core.http.controller import BaseController


class ControllerManager:
    def __init__(self, controllers: List[Type[BaseController]] | None = None):
        self.controllers = controllers or []

    def add_controller(self, controller):
        self.controllers.append(controller)
        return controller

    def setup_all_dependencies(self):
        for controller in self.controllers:
            controller.setup_dependencies()
            controller.init()

    def register_routers(self, app: FastAPI):
        for controller in self.controllers:
            app.include_router(controller.router)