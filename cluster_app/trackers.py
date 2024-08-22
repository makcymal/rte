import os
import json
import psutil as ps
import logging
from abc import abstractmethod, ABC
from collections import namedtuple

from utils import Subscriber
from query import Query
import config


logger = logging.getLogger(__name__)


class Tracker(Subscriber, ABC):

    __slots__ = (
        "interval",
        "bytes_denom",
        "specs",
        "fields",
        "extended",
        "prev",
    )

    def __init__(self):
        Query().subscribe(self)
        self.get_update()
        self.specs = {}
        self._fill_specs()
        logger.info(f"Got {str(self)} specs")

    def get_update(self):
        query = Query()
        self.interval = query["interval"]
        if m := query["measure"] == "kb":
            self.bytes_denom = 1024
        elif m == "mb":
            self.bytes_denom = 1024 * 1024
        else:
            self.bytes_denom = 1
        self.extended = query[f"{str(self)}_extended"]
        self.fields = set(query[f"{str(self)}_fields"])
        self._validate_query_fields()
        self.prev = None

        logger.info(f"{str(self)}_tracker updated query")

    def _validate_query_fields(self):
        invalid_fields = self.fields.difference(self.__class__.VALID_FIELDS)
        if invalid_fields:
            logger.warning(
                f"Got invalid fields in query for {self.__class__.__name__}: {list(invalid_fields)}, they will be ignored"
            )
            self.fields.difference_update(invalid_fields)

    def _debug_tracking(self, response):
        if config.DEBUG:
            with open(f"{str(self)}.json", "w") as file:
                json.dump(response, file, indent=4)

    @abstractmethod
    def _fill_specs(self):
        pass

    @abstractmethod
    def track(self) -> dict | list[dict]:
        pass


class CpuTracker(Tracker):

    VALID_FIELDS = set(
        (
            "system",
            "user",
            "nice",
            "idle",
            "iowait",
            "irq",
            "softirq",
            "steal",
            "guest",
            "guest_nice",
            "freq",
        )
    )

    def __str__(self) -> str:
        return "cpu"

    def _get_response(self) -> dict:
        response = {}

        cpu_times = ps.cpu_times_percent(percpu=False)
        cpu_times_fields = self.fields.intersection(cpu_times._fields)
        response = {field: getattr(cpu_times, field) for field in cpu_times_fields}

        if "freq" in self.fields:
            cpu_freq = ps.cpu_freq(percpu=False)
            response["freq"] = round(
                cpu_freq.current * 1000 if cpu_freq.current < 10 else cpu_freq.current
            )

        return response

    def _get_response_percpu(self) -> list[dict]:
        response = []

        cpu_times_percpu = ps.cpu_times_percent(percpu=True)
        if cpu_times_percpu:
            cpu_times_fields = self.fields.intersection(cpu_times_percpu[0]._fields)
            response = [
                {field: getattr(cpu_times, field) for field in cpu_times_fields}
                for cpu_times in cpu_times_percpu
            ]
        else:
            logger.error(
                "Cannot get psutil.cpu_times_percent(percpu=True): got empty list"
            )

        if "freq" in self.fields:
            cpu_freq_percpu = ps.cpu_freq(percpu=True)
            for core_response, freq in zip(response, cpu_freq_percpu):
                core_response["freq"] = round(
                    freq.current * 1000 if freq.current < 10 else freq.current
                )

        return response

    def track(self) -> dict | list[dict]:
        response = (
            self._get_response_percpu() if self.extended else self._get_response()
        )

        self._debug_tracking(response)
        return response


class NetTracker(Tracker):

    FIELDS_MAP = {
        "recv": "bytes_recv",
        "sent": "bytes_sent",
        "errin": "errin",
        "errout": "errout",
        "dropin": "dropin",
        "dropout": "dropout",
    }
    VALID_FIELDS = set(FIELDS_MAP.keys())

    def __str__(self):
        return "net"

    def _fill_specs(self):
        self.specs["nics"] = list(ps.net_io_counters(pernic=True).keys())

    def _get_io(self, io: namedtuple, prev: namedtuple) -> dict:
        mp = self.__class__.FIELDS_MAP
        response = {
            field: round(
                (getattr(io, mp[field]) - getattr(prev, mp[field])) / self.interval
            )
            for field in self.fields
        }
        return response

    def _get_response(self) -> dict:
        net_io = ps.net_io_counters(pernic=False)
        response = self._get_io(net_io, self.prev) if self.prev else {}
        self.prev = net_io
        return response

    def _get_response_pernic(self) -> dict:
        net_io_pernic = ps.net_io_counters(pernic=True)
        response = (
            {
                nic: self._get_io(net_io, self.prev[nic])
                for nic, net_io in net_io_pernic.items()
            }
            if self.prev
            else {}
        )
        self.prev = net_io_pernic
        return response

    def track(self) -> dict:
        response = (
            self._get_response_pernic() if self.extended else self._get_response()
        )

        self._debug_tracking(response)
        return response


# отслеживание мемов в паблике караси БЕСПЛАТНО
# https://vk.com/public203309877
class MemTracker(Tracker):

    VALID_FIELDS = set(("used", "buffers", "cached", "shared", "swap"))

    def __str__(self):
        return "mem"

    def _fill_specs(self):
        self.specs["mem_total"] = round(ps.virtual_memory().total / self.bytes_denom)
        self.specs["swp_total"] = round(ps.swap_memory().total / self.bytes_denom)

    def _getattr(self, field: str, mem: namedtuple, swp: namedtuple) -> float:
        if field == "swap":
            return swp.used if self.extended else swp.percent
        elif field == "used":
            return mem.used if self.extended else mem.percent
        else:
            return (
                round(getattr(mem, field) / self.bytes_denom)
                if self.extended
                else round(getattr(mem, field) * 100 / mem.total, 1)
            )

    def track(self) -> dict:
        mem = ps.virtual_memory()
        swp = ps.swap_memory()
        response = {field: self._getattr(field, mem, swp) for field in self.fields}

        self._debug_tracking(response)
        return response


class DskTracker(Tracker):

    VALID_FIELDS = set(("used", "read", "write"))

    def __str__(self):
        return "dsk"

    def _fill_specs(self):
        partitions = ps.disk_partitions()
        self.specs = [
            {
                "name": os.path.basename(part.device),
                "mountpoint": part.mountpoint,
                "total": round(ps.disk_usage(part.mountpoint).total / self.bytes_denom),
            }
            for part in partitions
        ]

    def _get_response(self):
        response = {}
        if "used" in self.fields:
            response["used"] = round(
                sum(ps.disk_usage(spec["mountpoint"]).used for spec in self.specs)
                / self.bytes_denom
            )

        disk_io = ps.disk_io_counters(perdisk=False)
        if "read" in self.fields:
            if self.prev:
                response["read"] = round(
                    (disk_io.read_bytes - self.prev.read_bytes)
                    / self.bytes_denom
                    / self.interval
                )
        if "write" in self.fields:
            if self.prev:
                response["write"] = round(
                    (disk_io.write_bytes - self.prev.write_bytes)
                    / self.bytes_denom
                    / self.interval
                )

        self.prev = disk_io
        return response

    def _get_response_perdisk(self):
        names = [spec["name"] for spec in self.specs]
        if not self.fields:
            return {}
        response = {name: {} for name in names}

        if "used" in self.fields:
            for name, spec in zip(names, self.specs):
                response[name].update(
                    used=round(
                        ps.disk_usage(spec["mountpoint"]).used / self.bytes_denom
                    )
                )

        disk_io = ps.disk_io_counters(perdisk=True)
        if "read" in self.fields:
            if self.prev:
                for name in names:
                    response[name].update(
                        read=round(
                            (disk_io[name].read_bytes - self.prev[name].read_bytes)
                            / self.bytes_denom
                            / self.interval
                        )
                    )
        if "write" in self.fields:
            if self.prev:
                for name in names:
                    response[name].update(
                        write=round(
                            (disk_io[name].write_bytes - self.prev[name].write_bytes)
                            / self.bytes_denom
                            / self.interval
                        )
                    )

        self.prev = disk_io
        return response

    def track(self) -> dict:
        response = (
            self._get_response_perdisk() if self.extended else self._get_response()
        )

        self._debug_tracking(response)
        return response


def all_trackers() -> tuple[CpuTracker, NetTracker, MemTracker, DskTracker]:
    return (CpuTracker(), NetTracker(), MemTracker(), DskTracker())
