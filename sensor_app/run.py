import sys
import time
import json
import logging
import asyncio as aio
from asyncio import CancelledError

import config
from connection import Connection, CONN_ERROR
from prompt import PromptStore
from sensor import all_trackers


logger = logging.getLogger(__name__)

conn = Connection()
prompt_lock = aio.Lock()
prompt_store = PromptStore()
trackers = all_trackers()


async def send_specs():
    specs = json.dumps(
        {
            "type": "specs",
            "group": config.GROUP,
            "machine": config.MACHINE,
            **{str(tracker): tracker.specs() for tracker in trackers},
        }
    )
    await conn.sendall(specs)
    logger.info("Sent specs to backend")


async def send_reports():
    interval = 1
    while True:
        async with prompt_lock:
            prompt = prompt_store.get_prompt()
            report = json.dumps(
                {
                    "type": "report",
                    "group": config.GROUP,
                    "machine": config.MACHINE,
                    "time": round(time.time()),
                    "mark": prompt_store.mark,
                    **{str(tracker): tracker.report(prompt) for tracker in trackers},
                }
            )
            await conn.sendall(report)
            logger.info("Sent report to backend")
            interval = prompt.interval
        await aio.sleep(interval)


async def recv_prompts():
    while True:
        prompt_str = await conn.recvall()
        logger.debug(f"Received prompt: {prompt_str}")
        async with prompt_lock:
            prompt_store.add_prompt(prompt_str)


async def aio_task(func):
    try:
        await func()
    except CancelledError:
        logger.debug(f"Task {func.__name__} cancelled")


async def main():
    if len(sys.argv) >= 2:
        config.GROUP = sys.argv[1]
    if len(sys.argv) >= 3:
        config.MACHINE = sys.argv[2]

    logging.basicConfig(
        filename=config.logfile,
        level=config.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    logger.info(f"Current machine is <{config.MACHINE}> in group <{config.GROUP}>")

    await conn.establish()

    while True:
        try:
            tasks = aio.gather(aio_task(send_reports), aio_task(recv_prompts))
            logger.debug("send_reports and recv_prompts scheduled")
            await tasks
        except CONN_ERROR:
            logger.warning("Connection lost, trying to reconnect")
            tasks.cancel()
            await conn.establish()


if __name__ == "__main__":
    aio.run(main())
