import json
import psutil as ps
from py3nvml import py3nvml as nvidia
import os

from config import SENSOR_CATEGORIES


class CategorySpecs:
    @staticmethod
    def load_dict(specs_dict: dict):
        self = __class__()
        for attr in self.__class__.__slots__:
            setattr(self, attr, specs_dict.get(attr, None))

    def dump_dict(self) -> dict:
        specs = {}
        for attr in self.__class__.__slots__:
            value = getattr(self, attr)
            if value is not None:
                specs[attr] = value


class CpuSpecs(CategorySpecs):
    __slots__ = ("physical_cores", "logical_cores", "min_frequency", "max_frequency")

    @staticmethod
    def read():
        self = CpuSpecs()
        self.physical_cores = ps.cpu_count(logical=False)
        self.logical_cores = ps.cpu_count(logical=True)

        cpu_freq = ps.cpu_freq(percpu=True)
        self.min_frequency = [each_freq.min for each_freq in cpu_freq]
        self.max_frequency = [each_freq.max for each_freq in cpu_freq]


class GpuSpecs(CategorySpecs):
    __slots__ = ("graphics_processing_units",)

    def read(self):
        count = nvidia.nvmlDeviceGetCount()
        self.gpus = []
        for idx in range(count):
            handle = nvidia.nvmlDeviceGetHandleByIndex(idx)
            self.gpus.append(
                {
                    "name": nvidia.nvmlDeviceGetName(handle),
                    "memory_volume": nvidia.nvmlDeviceGetMemoryInfo(handle).total,
                }
            )


class NetSpecs(CategorySpecs):
    __slots__ = ("interfaces",)

    def read(self):
        self.interfaces = list(ps.net_io_counters(pernic=True).keys())


class RamSpecs(CategorySpecs):
    __slots__ = ("ram_volume", "swap_volume")

    def read(self):
        self.ram_volume = ps.virtual_memory().total
        self.swap_volume = ps.swap_memory().total


class NvmSpecs(CategorySpecs):
    __slots__ = ("disks",)

    def read(self):
        self.disks = [
            {
                "name": os.path.basename(prt.device),
                "mountpoint": prt.mountpoint,
                "disk_volume": round(
                    ps.disk_usage(prt.mountpoint).total / self.bytes_denom
                ),
            }
            for prt in ps.disk_partitions()
        ]


class CpuReport:
    __slots__ = ("specs", "fields", "detailed")

    def __init__(self) -> None:
        self.specs = CpuSpecs()
        self.specs.read()
