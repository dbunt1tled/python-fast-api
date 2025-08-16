import asyncio
from typing import Any, ClassVar

from fastapi import WebSocket, status

from src.core.log.log import Log


class WSManager:
    MAX_CONNECTIONS: ClassVar[int] = 1000
    def __init__(
        self,
        log: Log,
    ) -> None:
        self._connections: dict[str, list[tuple[WebSocket, asyncio.Lock]]] = {}
        self._lock = asyncio.Lock()
        self.log = log

    async def connect(self, user_id: str, websocket: WebSocket) -> None:
        if len(self._connections) >= self.MAX_CONNECTIONS:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)  # Connection limit exceeded
            self.log.error(f"🥕 WebSocket connect: user {user_id}, connection limit exceeded")
            return
        await websocket.accept()
        async with self._lock:
            lock = asyncio.Lock()
            self._connections.setdefault(user_id, []).append((websocket, lock))
        self.log.info(f"🍏 WebSocket connected: {user_id} (total {len(self._connections.get(user_id, []))})")

    async def disconnect(self, user_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(user_id, [])
            conns = [c for c in conns if c[0] is not websocket]
            if not conns:
                self._connections.pop(user_id, None)
            try:
                await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
            except Exception as e:
                self.log.warning(f"🫜 WebSocket failed to close to {user_id}: {e}")
        self.log.info(f"🍎 WebSocket disconnected: {user_id}")

    async def send_to_user(self, user_id: str, data: dict[str, Any], websocket: WebSocket | None = None) -> int:
        conns = self._connections.get(user_id, [])
        if not conns:
            self.log.debug(f"🍊 WebSocket No active ws for user {user_id}")
            return 0
        if websocket is not None:
            wss = [c for c in conns if c[0] is websocket]
            if not wss:
                self.log.debug(f"🍊 WebSocket No active ws for user {user_id}")
                return 0
            success = int(await self._safe_send(wss[0], data, user_id))
        else:
            coros = [self._safe_send(ws, data, user_id) for ws in conns]
            results = await asyncio.gather(*coros, return_exceptions=True)
            success = sum(1 for r in results if r is True)
        self.log.info(f"🍐 WebSocket sent message to {success}/{len(conns)} connections for user {user_id}")
        return success

    async def broadcast(self, data: dict[str, Any], exclude_user_id: list[str] | None = None) -> int:
        if exclude_user_id is None:
            exclude_user_id = []
        success = 0
        user_ids = []
        for user_id in self._connections.keys():
            if user_id in exclude_user_id:
                continue
            success += await self.send_to_user(user_id, data)
            user_ids.append(user_id)
        self.log.info(f"🍐 WebSocket sent messages to {success} connections for users {user_ids}")
        return success

    async def _safe_send(self, ws: tuple[WebSocket, asyncio.Lock], data: dict[str, Any], user_id: str) -> bool:
        try:
            async with ws[1]:
                await ws[0].send_json(data)
                return True
        except Exception as exc:
            self.log.warning(f"🌶️ WebSocket failed to send to {user_id}: {exc}")
            # best-effort cleanup
            await self.disconnect(user_id, ws[0])
            try:
                await ws[0].close()
            except Exception as e:
                self.log.warning(f"🫜 WebSocket failed to close to {user_id}: {e}")
            return False

    async def close_all(self) -> None:
        async with self._lock:
            conns = [(uid, s) for uid, s in self._connections.items()]
            self._connections.clear()
        coros = []
        for uid, socks in conns:
            for ws in socks:
                try:
                    coros.append(ws[0].close())
                except Exception as e:
                    self.log.warning(f"🫜 WebSocket failed to close to {uid}: {e}")
        if coros:
            await asyncio.gather(*coros, return_exceptions=True)
        self.log.info("🥝 WebSocket Closed all websockets")
