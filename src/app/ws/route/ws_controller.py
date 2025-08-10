import json

from fastapi import FastAPI
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.core.di.container import Container
from src.core.http.controller import BaseController


class WSController(BaseController):
    def __init__(self, app: FastAPI, container: Container) -> None:
        super().__init__(container=container)
        app.add_api_websocket_route(path="/ws/{user_id}", endpoint=self.connect)

    async def connect(
        self,
        websocket: WebSocket,
        user_id: str,
    ) -> None:
        ws_service = self.container.ws_service()
        try:
            await ws_service.add_connection(user_id, websocket)
            async for data in websocket.iter_text():
                try:
                    message = json.loads(data)

                    await ws_service.process_message(user_id=user_id, message=message, websocket=websocket)

                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    self.logger.warning(f"Invalid JSON received from user {user_id}")
                except Exception as e:
                    self.logger.error(f"Error handling WebSocket message from user {user_id}: {e}")
                    break

        except Exception as e:
            self.logger.error(f"WebSocket error for user {user_id}: {e}")
        finally:
            await ws_service.remove_connection(user_id=user_id, websocket=websocket)
