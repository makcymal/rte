import json
import pathlib

JSON_FALLBACK = pathlib.Path(__file__).parent / "prompt.fallback.json"
JSON_STANDARD = pathlib.Path(__file__).parent / "prompt.standard.json"
JSON_EXTENDED = pathlib.Path(__file__).parent / "prompt.extended.json"

PAYLOAD_CATEGORIES = ["cpu", "net", "mem", "dsk", "gpu"]
AVAIL_FIELDS = {
    cat: set(json.load(open(JSON_FALLBACK, "r"))[cat]["units"].keys())
    for cat in PAYLOAD_CATEGORIES
}


class Prompt:
    __slots__ = ("mark", "interval", *PAYLOAD_CATEGORIES)

    def __init__(self, **kwargs):
        self.load_fallback()

        if len(kwargs) == 1:
            match next(iter(kwargs.keys())):
                case "prompt_filename":
                    with open(kwargs["prompt_filename"], "r") as prompt_file:
                        prompt_dict = json.load(prompt_file)
                case "prompt_str":
                    prompt_dict = json.loads(kwargs["prompt_str"])
                case "prompt_dict":
                    prompt_dict = kwargs["prompt_dict"]
            self.merge_dict(prompt_dict)

    def load_fallback(self):
        with open(JSON_FALLBACK, "r") as prompt_file:
            prompt_dict = json.load(prompt_file)
        self.mark = prompt_dict["mark"]
        self.interval = prompt_dict["interval"]
        for cat in PAYLOAD_CATEGORIES:
            setattr(self, cat, CategoryPrompt(cat, prompt_dict[cat]))

    def validate(self):
        for cat in PAYLOAD_CATEGORIES:
            getattr(self, cat).validate()

    def merge(self, other_prompt):
        self.interval = other_prompt.interval
        for cat in PAYLOAD_CATEGORIES:
            getattr(self, cat).merge(getattr(other_prompt, cat))

    def merge_dict(self, other_dict: dict):
        if "interval" in other_dict:
            self.interval = other_dict["interval"]
        for cat in PAYLOAD_CATEGORIES:
            cat_prompt = CategoryPrompt(cat, other_dict.get(cat, None))
            cat_prompt.validate()
            getattr(self, cat).merge(cat_prompt)

    def __str__(self) -> str:
        return "\n".join(
            ["Prompt:"] + [str(getattr(self, cat)) for cat in PAYLOAD_CATEGORIES]
        )


class CategoryPrompt:
    __slots__ = ("cat", "fields", "detailed", "units")

    def __init__(self, cat: str, prompt_dict: dict | None):
        self.cat = cat
        if prompt_dict:
            for attr in self.__class__.__slots__[1:]:
                setattr(self, attr, prompt_dict.get(attr, None))
        else:
            for attr in self.__class__.__slots__[1:]:
                setattr(self, attr, None)

    def validate(self):
        ins_idx = 0
        if self.fields:
            for idx, field in enumerate(self.fields):
                if field in AVAIL_FIELDS[self.cat]:
                    self.fields[ins_idx] = self.fields[idx]
                    ins_idx += 1
            self.fields = self.fields[:ins_idx]

        if self.detailed not in (None, 0, 1):
            self.detailed = 0

    def merge(self, other_prompt):
        if other_prompt.fields:
            self.fields = other_prompt.fields
        if other_prompt.detailed:
            self.detailed = other_prompt.detailed
        if other_prompt.units:
            self.units.update(other_prompt.units)

    def merge_dict(self, other_dict: dict | None):
        if "fields" in other_dict:
            self.fields = other_dict["fields"]
        if "detailed" in other_dict:
            self.detailed = other_dict["detailed"]
        if "units" in other_dict:
            self.units.update(other_dict["units"])

    def __str__(self) -> str:
        return "\n".join(
            [
                f"{self.cat.capitalize()}Prompt:",
                f"\tfields: {self.fields}",
                f"\tdetailed: {self.detailed}",
                f"\tunits: {self.units}",
            ]
        )


FALLBACK_PROMPT = Prompt()
STANDARD_PROMPT = Prompt(prompt_filename=JSON_STANDARD)
EXTENDED_PROMPT = Prompt(prompt_filename=JSON_EXTENDED)
