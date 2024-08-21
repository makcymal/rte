#!/home/makcymal/miniconda3/envs/web/bin/python

import os
import pathlib
import sys
import time
import json
import struct
import logging
import asyncio as aio
from asyncio import CancelledError

from query import Query
from trackers import all_trackers
from utils import Singleton
import config


CONN_ERROR = (OSError, BrokenPipeError, ConnectionResetError)
query_lock = aio.Lock()
logger = logging.getLogger(__name__)


class Conn(metaclass=Singleton):
	__slots__ = ("reader", "writer", "rlock", "wlock")

	def __init__(self):
		self.reader = None
		self.writer = None
		self.rlock = aio.Lock()
		self.wlock = aio.Lock()

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
		async with self.rlock:
			raw_size = await self.reader.read(4)
			if raw_size == b"":
				raise ConnectionResetError
			size = struct.unpack("i", raw_size)[0]

			data = await self.reader.read(size)
			data = data.decode(encoding="utf-8")
			logger.info(f"Received: {data}")
			return data

	async def sendall(self, data: str):
		async with self.wlock:
			data = data.encode(encoding="utf-8")
			size = struct.pack("i", len(data))

			self.writer.write(size)
			await self.writer.drain()

			self.writer.write(data)
			await self.writer.drain()
			# logger.info(f"Sent: {data}")


async def send_responses():
	conn = Conn()
	query = Query()
	trackers = all_trackers()
	id = f"{config.BATCH}!{config.LABEL}"

	specs = json.dumps(
		{
			"header": f"spec!{id}",
			**{str(tracker): tracker.specs for tracker in trackers},
		}
	)
	await conn.sendall(specs)
	logger.info("Sent specs")

	while True:
		async with query_lock:
			response = json.dumps(
				{
					"header": f"resp!{id}!{query['mark']}!{round(time.time())}",
					**{str(tracker): tracker.track() for tracker in trackers},
				}
			)
			await conn.sendall(response)
			# logger.info("Sent response")
			interval = query["interval"]
		await aio.sleep(interval)


async def send_responses_wrapper():
	try:
		await send_responses()
	except CancelledError:
		logger.info("send_responses cancelled")


async def recv_queries():
	conn = Conn()
	query = Query()

	while True:
		logger.info("Ready to receive queries")
		query_str = await conn.recvall()
		async with query_lock:
			if query_str == "stop":
				continue
			query.update(query_str)
			logger.debug(f"Query updated: {query_str}")


async def recv_queries_wrapper():
	try:
		await recv_queries()
	except CancelledError:
		logger.info("send_responses cancelled")


async def main():
	if len(sys.argv) >= 2:
		config.BATCH = sys.argv[1]
	if len(sys.argv) >= 3:
		config.LABEL = sys.argv[2]

	query = Query()

	logging.basicConfig(
		filename=query.logfile,
		level=query.loglevel,
		format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
		datefmt="%H:%M:%S",
	)

	logger.info(f"Current machine is: {config.BATCH}!{config.LABEL}")

	conn = Conn()
	await conn.establish()

	while True:
		try:
			tasks = aio.gather(send_responses_wrapper(), recv_queries_wrapper())
			logger.info("send_responses and recv_queries scheduled")
			await tasks
		except CONN_ERROR:
			logger.warning("Connection lost, trying to reconnect")
			tasks.cancel()
			await conn.establish()


if __name__ == "__main__":
	aio.run(main())
