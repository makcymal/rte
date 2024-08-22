import json
from copy import deepcopy as cp
from utils import Publisher, Singleton

import logging

logger = logging.getLogger(__name__)


class FixedCpuPrompt:
    __slots__ = (
        "fields",
        "detailed",
        "system",
        "user",
        "nice",
        "iowait",
        "idle",
        "irq",
        "softirq",
        "steal",
        "guest",
        "guest_nice",
        "freq",
    )

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def fallback(self):
        self.fields = ["system", "user", "iowait", "idle", "freq"]
        self.detailed = False
        self.system = "%"
        self.user = "%"
        self.nice = "%"
        self.iowait = "%"
        self.idle = "%"
        self.irq = "%"
        self.softirq = "%"
        self.steal = "%"
        self.guest = "%"
        self.guest_nice = "%"
        self.freq = "hz"


class FixedNetPrompt:
    __slots__ = (
        "fields",
        "detailed",
        "recv",
        "sent",
        "errin",
        "errout",
        "dropin",
        "dropout",
    )

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def fallback(self):
        self.fields = ["recv", "sent"]
        self.detailed = 0
        self.recv = "kb"
        self.sent = "kb"
        self.errin = "pcs"
        self.errout = "pcs"
        self.dropin = "pcs"
        self.dropout = "pcs"


class FixedMemPrompt:
    __slots__ = ("fields", "used", "buffers", "cached", "shared", "swap")

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def fallback(self):
        self.fields = ["used", "swap"]
        self.used = "kb"
        self.buffers = "kb"
        self.cached = "kb"
        self.shared = "kb"
        self.swap = "kb"


class FixedDskPrompt:
    __slots__ = ("fields", "per_dsk", "used", "read", "write")

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def fallback(self):
        self.fields = ["read", "write"]
        self.detailed = 0
        self.used = "kb"
        self.read = "kb"
        self.write = "kb"


class FixedGpuPrompt:
    __slots__ = ("fields" "per_gpu", "load", "memory")

    def __init__(self):
        for attr in self.__slots__:
            setattr(self, attr, None)

    def fallback(self):
        self.fields = ["load", "memory"]
        self.detailed = 0
        self.load = "%"
        self.memory = "mb"


class FixedPrompt:
    __slots__ = ("mark", "interval", "cpu", "net", "mem", "dsk", "gpu")


FALLBACK_PROMPT = {
    "mark": "fallback",
    "interval": 3,
    "cpu": {
        "fields": ["system", "user", "iowait", "idle", "freq"],
        "per_cpu": 0,
        "system": "%",
        "user": "%",
        "nice": "%",
        "iowait": "%",
        "idle": "%",
        "irq": "%",
        "softirq": "%",
        "steal": "%",
        "guest": "%",
        "guest_nice": "%",
        "freq": "hz",
    },
    "net": {
        "fields": ["recv", "sent"],
        "per_nic": 0,
        "recv": "kb",
        "sent": "kb",
        "errin": "pcs",
        "errout": "pcs",
        "dropin": "pcs",
        "dropout": "pcs",
    },
    "mem": {
        "fields": ["used", "swap"],
        "used": "kb",
        "buffers": "kb",
        "cached": "kb",
        "shared": "kb",
        "swap": "kb",
    },
    "dsk": {
        "fields": ["read", "write"],
        "per_dsk": 0,
        "used": "kb",
        "read": "kb",
        "write": "kb",
    },
    "gpu": {"fields": ["load", "memory"], "per_gpu": 0, "load": "%", "memory": "mb"},
}


class Prompt(Publisher, metaclass=Singleton):
    __slots__ = (
        "prompt",
        "fallback",
    )

    def __init__(self):
        super().__init__()

        with open("prompt.fallback.json", "r") as fallback_file:
            self.fallback = json.load(fallback_file)
            self.prompt = cp(self.fallback)

        logger.info("Prompt initialized with fallback version since it's default")

    def update(self, prompt_str: str):
        self.prompt = json.loads(prompt_str)
        logger.debug(f"Prompt updated")
        self.notify_subs()

    def __getitem__(self, key: str):
        try:
            return self.prompt[key]
        except:
            self.prompt = cp(self.fallback)
            logger.warning("Invalid prompt, using fallback")
            logger.debug(f"Invalid prompt: {self.prompt}")
