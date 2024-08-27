import json
import logging
from fastapi import APIRouter, WebSocket
from store import (
    sensors,
    prompts,
    groups_list,
    start_monitoring,
    stop_monitoring,
    edit_prompt,
)
from pathlib import Path


logger = logging.getLogger(__name__)

ws_router = APIRouter()


@ws_router.websocket("/ws")
async def handle_client(ws: WebSocket):
    await ws.accept()

    while True:
        try:
            query = json.loads(await ws.receive_text())

            match query["type"]:
                case "groups_list":
                    await send_groups(ws)

                case "prompt_desc":
                    mark = query["mark"]
                    await send_prompt_desc(ws, mark)

                case "prompt_avail_fields":
                    await send_prompt_avail_fields(ws)

                case "edit_prompt":
                    mark = query["mark"]
                    new_prompt = query["new_prompt"]
                    await edit_prompt(mark, new_prompt)

                case "machine_specs":
                    group = query["group"]
                    machine = query["machine"]
                    await send_machine_specs(ws, group, machine)

                case "start_monitoring":
                    group = query.get("group", "*")
                    machine = query.get("machine", "*")
                    mark = query["mark"]
                    await start_monitoring(ws, group, machine, mark)

                case "stop_monitoring":
                    await stop_monitoring(ws)
        except:
            break


async def send_groups(ws: WebSocket):
    response = {"type": "groups_list", "groups": groups_list}
    await ws.send_json(response)
    logger.debug(f"Sent groups to client {ws.client}")


async def send_prompt_desc(ws: WebSocket, mark: str):
    response = {"type": "prompt_desc", "prompt": prompts}
    await ws.send_json(response)


filename = Path(__file__).parent.parent / "json" / "prompt-avail-fields.json"
with open(filename, "r") as avail_fields_file:
    avail_fields = json.load(avail_fields_file)


async def send_prompt_avail_fields(ws):
    response = {"type": "prompt_avail_fields", "avail_fields": avail_fields}
    await ws.send_json(response)


async def send_machine_specs(ws: WebSocket, group: str, machine: str):
    response = {
        "type": f"machine_specs",
        "group": group,
        "machine": machine,
        **sensors[group][machine].specs,
    }
    await ws.send_json(response)
    logger.debug(f"Sent specs to client {ws.client}")
