import json
import logging
import asyncio as aio
from store import (
    add_sensor,
    add_report,
    send_report,
    PEER_DISCONNECTED,
    recvall,
)


logger = logging.getLogger(__name__)


# port used to listen to sensors
SENSORS_PORT = 32300


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

    type = specs["type"]
    if type == "specs":
        group = specs["group"]
        machine = specs["machine"]
        add_sensor(group, machine, reader, writer, specs)

    # recieving responses
    while True:
        if (report := json.loads(await recvall(reader))) == PEER_DISCONNECTED:
            break

        type = report["type"]
        if type == "report":
            group = report["group"]
            machine = report["machine"]
            mark = report["mark"]
            add_report(group, machine, mark, report)
            send_report(group, machine, mark)
