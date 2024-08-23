import asyncio as aio
import struct

import config

import logging

logger = logging.getLogger(__name__)
CONN_ERROR = (OSError, BrokenPipeError, ConnectionResetError)


class Connection:
    __slots__ = ("reader", "writer", "reader_lock", "writer_lock")

    def __init__(self):
        self.reader = None
        self.writer = None
        self.reader_lock = aio.Lock()
        self.writer_lock = aio.Lock()

    async def establish(self):
        while not self.writer or self.writer.is_closing():
            logger.info("Trying to establish connection")
            try:
                self.reader, self.writer = await aio.open_connection(
                    host=config.HOST_BACKEND,
                    port=config.PORT_BACKEND,
                )
            except CONN_ERROR:
                pass
            await aio.sleep(config.RECONNECT_DELAY)
        logger.info("Connection established")

    async def recvall(self) -> str:
        async with self.reader_lock:
            raw_size = await self.reader.read(4)
            if raw_size == b"":
                raise ConnectionResetError
            size = struct.unpack("i", raw_size)[0]

            data = await self.reader.read(size)
            data = data.decode(encoding="utf-8")
            logger.debug(f"Received: {data}")
            return data

    async def sendall(self, data: str):
        async with self.writer_lock:
            data = data.encode(encoding="utf-8")
            size = struct.pack("i", len(data))

            self.writer.write(size)
            await self.writer.drain()

            self.writer.write(data)
            await self.writer.drain()
            logger.debug(f"Sent: {data}")
