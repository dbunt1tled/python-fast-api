import asyncio
from typing import Any

from fastapi import WebSocket

from src.core.log.log import Log


class WSManager:
    def __init__(
            self,
            log: Log,
    ) -> None:
        self._connections: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()
        self.log = log

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            conns = self._connections.setdefault(user_id, set())
            conns.add(websocket)
        self.log.info(f"🍏 WebSocket connected: {user_id} (total {len(self._connections.get(user_id, []))})")

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(user_id)
            if not conns:
                return
            conns.discard(websocket)
            if not conns:
                self._connections.pop(user_id, None)
        self.log.info(f"🍎 WebSocket disconnected: {user_id}")

    async def send_to_user(self, user_id: str, data: dict[str, Any]) -> int:
        conns = list(self._connections.get(user_id, []))
        if not conns:
            self.log.debug(f"🍊 WebSocket No active ws for user {user_id}")
            return 0
        coros = [self._safe_send(ws, data, user_id) for ws in conns]
        results = await asyncio.gather(*coros, return_exceptions=True)
        success = sum(1 for r in results if r is True)
        self.log.info(f"🍐 WebSocket sent message to {success}/{len(conns)} connections for user {user_id}")
        return success

    async def broadcast(self, data: dict[str, Any], exclude_user_id: list[str] = []) -> int:
        success = 0
        user_ids = []
        for user_id in self._connections.keys():
            if user_id in exclude_user_id:
                continue
            success += await self.send_to_user(user_id, data)
            user_ids.append(user_id)
        self.log.info(f"🍐 WebSocket sent messages to {success} connections for users {user_ids}")
        return success

    async def _safe_send(self, ws: WebSocket, data: dict[str, Any], user_id: str) -> bool:
        try:
            await ws.send_json(data)
            return True
        except Exception as exc:
            self.log.warning(f"🌶️ WebSocket failed to send to {user_id}: {exc}")
            # best-effort cleanup
            await self.disconnect(user_id, ws)
            try:
                await ws.close()
            except Exception as e:
                self.log.warning(f"🫜 WebSocket failed to close to {user_id}: {e}")
            return False

    async def close_all(self) -> None:
        async with self._lock:
            conns = [(uid, list(s)) for uid, s in self._connections.items()]
            self._connections.clear()
        coros = []
        for uid, socks in conns:
            for ws in socks:
                try:
                    coros.append(ws.close())
                except Exception as e:
                    self.log.warning(f"🫜 WebSocket failed to close to {uid}: {e}")
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)
        self.log.info("🥝 WebSocket Closed all websockets")
