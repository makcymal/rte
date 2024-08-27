import psutil as ps
import json

from config import SENSOR_CATEGORIES
from prompt import Prompt, PromptStore

import logging


logger = logging.getLogger(__name__)


SPECS_SCHEME = json.load(open("scheme/specs.json", "r"))


def byte_converter(amount: int, into: str) -> float:
    match into:
        case "kb":
            amount = round(amount / 1024, 2)
        case "mb":
            amount = round(amount / 1024**2, 2)
        case "gb":
            amount = round(amount / 1024**3, 2)
        case "tb":
            amount = round(amount / 1024**4, 2)
    return amount


def mhz_converter(amount: float, into: str) -> float:
    amount = int(amount)
    match into:
        case "hz":
            amount *= 1024**2
        case "khz":
            amount *= 1024
        case "ghz":
            amount = round(amount / 1024, 2)
    return amount


class Tracker:
    __slots__ = "specs"

    def __init__(self):
        self.specs = self.get_specs()

    def track(self, prompt: Prompt):
        cat_prompt = getattr(prompt, self.__class__.CATEGORY)
        if not cat_prompt.detailed:
            report = self.get_report(cat_prompt.fields, cat_prompt.units)
        else:
            report = self.get_report_detailed(cat_prompt.fields, cat_prompt.units)
        return report


class CpuTracker(Tracker):
    CATEGORY = "cpu"

    def get_specs(self) -> dict:
        units = SPECS_SCHEME["cpu"]["units"]

        specs = {}
        specs["cores_phys"] = ps.cpu_count(logical=False)
        specs["cores_logic"] = ps.cpu_count(logical=True)

        cpu_freq = ps.cpu_freq(percpu=True)
        specs["min_freq"] = [
            mhz_converter(each_freq.min, units["min_freq"]) for each_freq in cpu_freq
        ]
        specs["max_freq"] = [
            mhz_converter(each_freq.max, units["max_freq"]) for each_freq in cpu_freq
        ]

        for field, value in specs.items():
            if units[field]:
                specs[field] = str(value) + " " + units[field]

        return specs

    def get_report(self, fields: list[str], units: dict) -> dict:
        report = {}

        cpu_times = ps.cpu_times_percent(percpu=False)
        report = {
            field: value
            for field in fields
            if (value := getattr(cpu_times, field, None)) is not None
        }

        if "freq" in fields:
            freq = ps.cpu_freq(percpu=False)
            report["freq"] = mhz_converter(freq.current, units["freq"])

        return report

    def get_report_detailed(self, fields: list[str], units: dict) -> list[dict]:
        report = []

        cpu_times_percpu = ps.cpu_times_percent(percpu=True)
        report = [
            {
                field: value
                for field in fields
                if (value := getattr(cpu_times, field, None)) is not None
            }
            for cpu_times in cpu_times_percpu
        ]

        if "freq" in fields:
            freq_percpu = ps.cpu_freq(percpu=True)
            for each_report, each_freq in zip(report, freq_percpu):
                each_report["freq"] = mhz_converter(each_freq.current, units["freq"])

        return report


def all_trackers():
    return [CpuTracker()]


from time import sleep

cpu = CpuTracker()

print(cpu.specs)

prompt_store = PromptStore()
prompt = prompt_store.get_prompt()

while True:
    report = cpu.track(prompt)
    print(report)
    sleep(2)
