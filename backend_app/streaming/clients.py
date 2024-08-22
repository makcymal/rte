import json
import logging
from fastapi import APIRouter, WebSocket
from streaming.store import clients, sensors


logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws")
async def handle_client(ws: WebSocket):
    """
    Client can send one of the followings messages:
    "lsob" - get LiSt Of Batches
    "head?BATCH" - get table HEADer for BATCH
    "mstd?BATCH" - STanDard Monitoring subscribe to BATCH
    "spec?BATCH?LABEL" - get SPECifications of machine with LABEL in BATCH
    "desc?BATCH?LABEL" - DESCribe fields for specific machine with LABEL in BATCH
    "mext?BATCH?LABEL" - EXTended Monitoring to machine with LABEL in BATCH
    "stop" - stop subscription
    """

    # websocket connecting
    await clients.connect(ws)

    while True:
        try:
            msg = await ws.receive_text()
            logger.info(f"Client requests {msg}")

            match msg[:4]:
                case "lsob":
                    await send_batches(ws)
                case "head":
                    batch = msg.split("?")[1]
                    await send_table_header(ws, batch)
                case "mstd":
                    batch = msg.split("?")[1]
                    clients.subscribe(ws, batch)
                case "spec":
                    batch, label = msg.split("?")[1:3]
                    await send_spec(ws, batch, label)
                case "desc":
                    batch, label = msg.split("?")[1:3]
                    await send_description(ws, batch, label)
                case "mext":
                    batch, label = msg.split("?")[1:3]
                    clients.subscribe(ws, f"{batch}!{label}")
                case "stop":
                    clients.unsubscribe(ws)

        except:
            clients.disconnect(ws)
            break


async def send_batches(ws: WebSocket):
    resp = {"header": "lsob", "batches": sensors.batches}
    await ws.send_json(resp)
    logger.info(f"Sent batches to client {ws.client}")


async def send_spec(ws: WebSocket, batch: str, label: str):
    resp = {"header": f"spec!{batch}!{label}", **sensors.get_specs(batch, label)}
    await ws.send_json(resp)
    logger.info(f"Sent specs to client {ws.client}")


with open("json/measures.standard.json", "r") as file:
    measures_std = json.load(file)
with open("json/measures.extended.json", "r") as file:
    measures_ext = json.load(file)


async def send_table_header(ws: WebSocket, batch: str):
    resp = {"header": f"head!{batch}", **measures_std}
    await ws.send_json(resp)
    logger.info(f"Sent table header to client {ws.client}")


async def send_description(ws: WebSocket, batch: str, label: str):
    resp = {"header": f"desc!{batch}!{label}", **measures_ext}
    await ws.send_json(resp)
    logger.info(f"Sent description to client {ws.client}")
