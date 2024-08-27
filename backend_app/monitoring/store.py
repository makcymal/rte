import json
import asyncio as aio
import struct
import secrets
import logging
from copy import deepcopy as cp
from fastapi import WebSocket
from dataclasses import dataclass


logger = logging.getLogger(__name__)


# random string indicating that sensor was disconnected
PEER_DISCONNECTED = f"{secrets.randbits(32)}"


@dataclass(frozen=True, slots=True)
class Sensor:
    reader: aio.StreamReader
    writer: aio.StreamWriter
    specs: dict
    
    
@dataclass(frozen=True, slots=True)
class PromptMeta:
    group: str
    machine: str
    mark: str


prompt_marks = ["group", "machine", "db"]


def load_prompts() -> dict:
    prompts_sources = {}
    for mark in prompt_marks:
        with open(f"../json/prompt.{mark}.json", "r") as prompt_file:
            prompts_sources[mark] = json.load(prompt_file)
    return prompts_sources


# sensors[group][machine] = Sensor(reader, writer, specs)
sensors = {}
# reports[mark][group][machine] = report as dict
reports = {mark: {} for mark in prompt_marks}
# prompt_sources[mark] = prompt as dict
prompt_sources = load_prompts()
# prompt_subs[group][machine][mark] = set[ws]
prompt_subs = {"*": {}}
# client_prompts[ws] = PromptMeta(group, machine, mark)
client_prompts = {}
# groups_list = list[group]
groups_list = []


async def start_monitoring(ws: WebSocket, group: str, machine: str, mark: str):
    stop_monitoring(ws)
    client_prompts[ws] = PromptMeta(group, machine, mark)
    prompt_subs[group][machine][mark].insert(ws)
    await send_mark(group, machine, mark, "add_prompt")
    
    
async def stop_monitoring(ws: WebSocket):
    if ws not in client_prompts:
        return
    meta = client_prompts[ws]
    prompt_subs[meta.group][meta.machine][meta.mark].discard(ws)
    del client_prompts[ws]
    await send_mark(meta.group, meta.machine, meta.mark, "del_prompt")
    

def add_sensor(
    group: str,
    machine: str,
    reader: aio.StreamReader,
    writer: aio.StreamWriter,
    specs: dict,
):
    if group not in sensors:
        groups_list.append(group)
        sensors[group] = {}
        
        prompt_subs[group] = {}
        prompt_subs[group]["*"] = {}
        
        for mark in prompt_marks:
            reports[mark][group] = {}
            
    if machine not in prompt_subs[group]:
        prompt_subs[group][machine] = {}
        
    sensors[group][machine] = Sensor(reader, writer, specs)


async def send_mark(group: str, machine: str, mark: str, type: str):
    async def single_send_mark(group: str, machine: str, mark: str, type: str):
        writer = sensors[group][machine].writer
        query = {"type": type, "mark": mark}
        await sendall(json.dumps(query), writer)
    
    if group == "*":
        for sns_group in sensors:
            for sns_machine in sensors[sns_group]:
                await single_send_mark(sns_group, sns_machine, mark)
    elif machine == '*':
        for sns_machine in sensors[group]:
            await single_send_mark(group, sns_machine, mark)
    else:
        await single_send_mark(group, machine, mark)

    
def add_report(group: str, machine: str, mark: str, report: dict):
    match mark:
        case "group":
            # reports[group][machine] = 
            ...
        
        case "machine":
            ...
            
        case "db":
            ...


def send_report(group: str, machine: str, mark: str):
    ...


class ResponseRepo:

    def insert(self, batch: str, label: str, resp: dict) -> str:
        logger.info(
            f"Sensor {batch}!{label} send response with header {resp['header']}"
        )
        proto, _batch, _label, mark, time = resp.pop("header").split("!")[:5]

        if mark == "std" or mark == "flb":
            header = f"mstd!{batch}!{label}!{time}"
            self.std[batch][label] = {"header": header, **resp}
            logger.info(f"Added mstd response from sensor {batch}!{label}")
            return "std"

        elif mark == "ext":
            header = f"mext!{batch}!{label}!{time}"
            self.ext[batch][label] = {"header": header, **resp}
            logger.info(f"Added mext response from sensor {batch}!{label}")

            # someone monitoring the whole batch including current particular machine
            if batch in prompts:
                self.std[batch][label] = {
                    "header": header,
                    **self.standartise_response(batch, label, resp),
                }
                logger.info(
                    f"There is batch {batch} in prompts so added mstd response from sensor {batch}!{label}"
                )
            return "ext"

    def _flatten_ext(self, resp: dict) -> dict:
        net = resp["net"]
        resp["net"] = [
            {
                "name": key,
                **val,
            }
            for key, val in net.items()
        ]

        mem = resp["mem"]
        resp["mem"] = [mem]

        dsk = resp["dsk"]
        resp["dsk"] = [
            {
                "name": key,
                **val,
            }
            for key, val in dsk.items()
        ]
        return resp

    def send_last(self, mark: str, batch: str, label: str):
        if mark == "std":
            logger.info(f"Sending last mstd response from sensor {batch}!{label}")
            clients.notify(batch, self.std[batch][label])
        elif mark == "ext":
            logger.info(f"Sending last mext response from sensor {batch}!{label}")
            clients.notify(
                f"{batch}!{label}", self._flatten_ext(self.ext[batch][label])
            )

    # when sensor sends only extended responses while we need both extended and standard
    # we can reduce amount of information in extended resp to make standard
    def standartise_response(self, batch: str, label: str, resp: dict) -> dict:
        cpu = self._standartise_cpu(resp["cpu"])
        net = self._standartise_net(resp["net"])
        mem = self._standartise_mem(batch, label, resp["mem"])
        dsk = self._standartise_dsk(resp["dsk"])
        return {"cpu": cpu, "net": net, "mem": mem, "dsk": dsk}

    def _standartise_cpu(cpu_percore: list[dict]) -> dict:
        cores = len(cpu_percore)
        if not cores:
            return {}

        cpu: dict = cp(cpu_percore[0])
        cpu_std_fields = set(prompts.std["cpu_fields"])
        for field in cpu:
            if field not in cpu_std_fields:
                cpu.pop(field)
            else:
                for i in range(1, cores):
                    cpu[field] += cpu_percore[i][field]
                cpu[field] /= cores

    def _standartise_net(net_pernic: dict) -> dict:
        nics = net_pernic.keys()
        if not nics:
            return {}

        net = cp(net_pernic[nics[0]])
        net_std_fields = set(prompts.std["net_fields"])
        for field in net.keys():
            if field not in net_std_fields:
                net.pop(field)
            else:
                for nic in nics:
                    net[field] += net_pernic[nic][field]

        return net

    def _standartise_mem(batch, label, mem_ext: dict) -> dict:
        mem = cp(mem_ext)
        # some fucking hardcode
        for field in ["buffers", "cached", "shared"]:
            mem.pop(field, None)
        if "used" in mem:
            mem["used"] = round(
                mem["used"] / sensors[batch][label]["mem"]["mem_total"] * 100, 1
            )
        if "swap" in mem:
            mem["swap"] = round(
                mem["swap"] / sensors[batch][label]["mem"]["swp_total"] * 100, 1
            )

        return mem

    def _standartise_dsk(dsk_perdisk: dict) -> dict:
        disks = dsk_perdisk.keys()
        if not disks:
            return {}

        dsk = cp(dsk_perdisk[disks[0]])
        dsk_std_fields = set(prompts.std["dsk_fields"])
        for field in dsk:
            if field not in dsk_std_fields:
                dsk.pop(field)
            else:
                for disk in disks:
                    dsk[field] += dsk_perdisk[disk][field]

        return dsk


class QueryRepo:
    __slots__ = ("std", "std_str", "ext", "ext_str", "query_set", "query_cnt")

    def __init__(self) -> None:
        with open("json/prompt.standard.json", "r") as std_file:
            self.std = json.load(std_file)
            self.std_str = json.dumps(self.std)
        with open("json/prompt.extended.json", "r") as ext_file:
            self.ext = json.load(ext_file)
            self.ext_str = json.dumps(self.ext)

        # all prompts existing right now
        self.query_set = set()
        # map prompt -> #{how much such a prompts exist}
        self.query_cnt = {}

    def __contains__(self, prompt: str) -> bool:
        return self.query_set.__contains__(prompt)

    def insert(self, prompt: str):
        # стандартный майкрософтовский энвелоуп
        self.query_set.add(prompt)
        if prompt not in self.query_cnt:
            self.query_cnt[prompt] = 0
            logger.info(f"Got new prompt {prompt}, updating it on sensors...")
        if self.query_cnt[prompt] == 0:
            aio.create_task(self.inject_query(prompt))
        self.query_cnt[prompt] += 1

    def remove(self, prompt: str):
        self.query_cnt[prompt] -= 1
        if self.query_cnt[prompt] == 0:
            self.query_set.remove(prompt)
            logger.info(f"Removed prompt {prompt}, updating it on sensors...")
            aio.create_task(self.seize_query(prompt))

    async def inject_query(self, prompt: str):
        tokens = prompt.split("!")

        if len(tokens) == 1:
            batch = prompt
            for label in sensors._ls[batch]:
                if f"{batch}!{label}" not in self.query_set:
                    sensor: Sensor = sensors._ls[batch][label]
                    await sendall(self.std_str, sensor.writer)
                else:
                    logger.info(
                        f"Didn't inject std prompt {prompt} to sensor {batch}!{label} since it has ext prompt"
                    )
        else:
            batch, label = tokens[:2]
            sensor: Sensor = sensors._ls[batch][label]
            await sendall(self.ext_str, sensor.writer)
            logger.info(f"Injected ext prompt {prompt} to sensor {batch}!{label}")

    async def seize_query(self, prompt: str):
        tokens = prompt.split("!")

        if len(tokens) == 1:
            batch = prompt
            for label in sensors._ls[batch]:
                if f"{batch}!{label}" not in self.query_set:
                    sensor: Sensor = sensors._ls[batch][label]
                    await sendall("stop", sensor.writer)
                    logger.info(
                        f"Seized std prompt {prompt} from sensor {batch}!{label}"
                    )
                else:
                    logger.info(
                        f"Didn't seize prompt {prompt} from sensor {batch}!{label} since it has ext prompt"
                    )
        else:
            batch, label = tokens[:2]
            sensor: Sensor = sensors._ls[batch][label]
            if batch in self.query_set:
                await sendall(self.std_str, sensor.writer)
                logger.info(
                    f"Replaces ext prompt {prompt} with std on sensor {batch}!{label}"
                )
            else:
                await sendall("stop", sensor.writer)
                logger.info(f"Seized ext prompt {prompt} from sensor {batch}!{label}")


clients = ClientSet()
sensors = SensorSet()
reports = ReportSet()
prompts = PromptSet()


async def recvall(reader: aio.StreamReader) -> str:
    raw_size = await reader.read(4)
    if raw_size == b"":
        return PEER_DISCONNECTED
    size = struct.unpack("i", raw_size)[0]

    data = await reader.read(size)
    data = data.decode(encoding="utf-8")
    return data


async def sendall(data: str, writer: aio.StreamWriter):
    data = data.encode(encoding="utf-8")
    size = struct.pack("i", len(data))

    writer.write(size)
    await writer.drain()

    writer.write(data)
    await writer.drain()
