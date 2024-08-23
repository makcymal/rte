import psutil as ps
import json

SENSOR_CATEGORIES = ["cpu", "net", "mem", "dsk", "gpu"]
SPECS_SCHEME = json.load(open("scheme/specs.json", "r"))


class CpuSpecs:
    __slots__ = SPECS_SCHEME['cpu']['fields']

    def __init__(self):
        self.cores_phys = ps.cpu_count(logical=False)
        self.cores_logic = ps.cpu_count(logical=True)

        cpu_freq = ps.cpu_freq(percpu=True)
        self.min_freq = [core.min for core in cpu_freq]
        self.max_freq = [core.max for core in cpu_freq]


class CpuSensor:
    __slots__ = (
        "specs",
        "prompts",
        "mark",
    )

    def __init__(self):
        self.specs = CpuSpecs()
        self.prompts = {"fallback": CpuPrompt()}
        self.mark = "fallback"

    def _report(self):
        report = {}

        cpu_times = ps.cpu_times_percent(percpu=False)
        report = {field: getattr(cpu_times, field) for field in self.prompts[self.mark].fields}

        if "freq" in self.fields:
            cpu_freq = ps.cpu_freq(percpu=False)
            report["freq"] = round(
                cpu_freq.current * 1000 if cpu_freq.current < 10 else cpu_freq.current
            )

        return report

    def _report_percpu(self):
        report = []

        cpu_times_percpu = ps.cpu_times_percent(percpu=True)
        report = [
            {field: getattr(cpu_times, field) for field in self.prompts[self.mark].fields}
            for cpu_times in cpu_times_percpu
        ]

        if "freq" in self.fields:
            cpu_freq_percpu = ps.cpu_freq(percpu=True)
            for each_report, freq in zip(report, cpu_freq_percpu):
                each_report["freq"] = round(
                    freq.current * 1000 if freq.current < 10 else freq.current
                )

        return report
    
    def get_report(self):
        if not self.prompt[self.mark].detailed:
            report = self._report()
        else:
            report = self._report_percpu()
        return report


def all_trackers():
    return []
