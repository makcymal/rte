import json
import logging
import asyncio as aio
from streaming.store import sensors, responses, PEER_DISCONNECTED, recvall, sendall


logger = logging.getLogger(__name__)


# port used to listen to sensors
SENSORS_PORT = 42400


# entry point for the communication with sensors
async def serve_sensors():
    server = await aio.start_server(handle_sensor, port=SENSORS_PORT)
    await server.serve_forever()


# initially recieves sensor specs
# then infinitely waits for responses from sensor
# another function in another event loop sends queries to sensors
async def handle_sensor(reader: aio.StreamReader, writer: aio.StreamWriter):
    logger.info(f"Connected {writer.get_extra_info('peername')}")
    # recieving specs
    specs = json.loads(await recvall(reader))
    proto, batch, label = specs.pop("header").split("!")[:3]
    sensors.insert(batch, label, reader, writer, specs)
    # recieving responses
    while True:
        if (resp := await recvall(reader)) == PEER_DISCONNECTED:
            break
        # trigger sending resp to client
        mark = responses.insert(batch, label, json.loads(resp))
        responses.send_last(mark, batch, label)
