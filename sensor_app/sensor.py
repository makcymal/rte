import psutil as ps


class CpuSpecs:
    __slots__ = ("cores_phys", "cores_logic", "min_freq", "max_freq")

    def __init__(self):
        self.cores_phys = ps.cpu_count(logical=False)
        self.cores_logic = ps.cpu_count(logical=True)

        cpu_freq = ps.cpu_freq(percpu=True)
        self.min_freq = [core.min for core in cpu_freq]
        self.max_freq = [core.max for core in cpu_freq]


class CpuPrompt:
    __slots__ = ("fields", "detailed", "units")

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

    def __init__(self, prompt=None):
        self.update(prompt)

    def update(self, prompt=None):
        if not prompt:
            self.to_fallback()
        else:
            try:
                self.fields = prompt["fields"]
                self.detailed = prompt["detailed"]
                self.units.update(prompt["units"])
                self.validate()
            except:
                self.to_fallback()
                
    def validate(self):
        ins_idx = 0
        for idx, field in enumerate(self.fields):
            if field in self.__class__.VALID_FIELDS:
                self.fields[ins_idx] = self.fields[idx]
                ins_idx += 1
        self.fields = self.fields[:ins_idx]
        
        if self.detailed not in (0, 1):
            self.detailed = 0
            
    def to_fallback(self):
        self.fields = ["system", "user", "iowait", "idle", "freq"]
        self.detailed = False
        self.units = {
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
        }


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

    def use_prompt(self, mark):
        if mark == self.mark:
            return
        elif mark not in self.prompts:
            self.mark = "fallback"
        else:
            self.mark = mark

    def update_prompt(self, mark, prompt):
        if mark in self.prompts:
            self.prompts[mark].update(prompt)
        else:
            self.prompts[mark] = prompt

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
