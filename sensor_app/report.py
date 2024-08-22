import os
import json
import psutil as ps
from py3nvml import py3nvml as nvml
from abc import abstractmethod, ABC
from collections import namedtuple

from utils import Subscriber
from prompt import Prompt
import config

import logging

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


def get_gpu_load():
    # Initialize NVML
    nvml.nvmlInit()

    # Get the number of GPUs
    device_count = nvml.nvmlDeviceGetCount()

    for i in range(device_count):
        # Get the handle for the device
        handle = nvml.nvmlDeviceGetHandleByIndex(i)

        # Get GPU utilization
        utilization = nvml.nvmlDeviceGetUtilizationRates(handle)

        print(f"GPU {i}:")
        print(f"  GPU Load: {utilization.gpu}%")
        print(f"  Memory Load: {utilization.memory}%")

    # Shutdown NVML
    nvml.nvmlShutdown()


if __name__ == "__main__":
    get_gpu_load()
