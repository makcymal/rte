import json
import pathlib

from config import SENSOR_CATEGORIES

import logging

logger = logging.getLogger(__name__)

JSON_FALLBACK = pathlib.Path(__file__).parent / "prompt.fallback.json"


class Prompt:
    __slots__ = ("mark", "interval", *SENSOR_CATEGORIES)

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
        for cat in SENSOR_CATEGORIES:
            setattr(self, cat, CategoryPrompt(cat, prompt_dict[cat]))

    def merge(self, other_prompt):
        self.interval = other_prompt.interval
        for cat in SENSOR_CATEGORIES:
            getattr(self, cat).merge(getattr(other_prompt, cat))

    def merge_dict(self, other_dict: dict):
        if "interval" in other_dict:
            self.interval = other_dict["interval"]
        for cat in SENSOR_CATEGORIES:
            cat_prompt = CategoryPrompt(cat, other_dict.get(cat, None))
            cat_prompt.validate()
            getattr(self, cat).merge(cat_prompt)

    def __str__(self) -> str:
        return "\n".join(
            ["Prompt:"] + [str(getattr(self, cat)) for cat in SENSOR_CATEGORIES]
        )


class CategoryPrompt:
    __slots__ = ("cat", "fields", "detailed")

    def __init__(self, cat: str, prompt_dict: dict | None):
        self.cat = cat
        if prompt_dict is None:
            prompt_dict = {}
        self.fields = prompt_dict.get("fields", None)
        self.detailed = prompt_dict.get("detailed", None)

    def merge(self, other_prompt):
        if other_prompt.fields:
            self.fields = other_prompt.fields
        if other_prompt.detailed:
            self.detailed = other_prompt.detailed

    def __str__(self) -> str:
        return "\n".join(
            [
                f"{self.cat.capitalize()}Prompt:",
                f"\tfields: {self.fields}",
                f"\tdetailed: {self.detailed}",
            ]
        )


class PromptStore:
    __slots__ = ("prompts", "mark")

    def __init__(self):
        self.prompts = {"fallback": Prompt()}
        self.mark = "fallback"

    def set_prompt(self, prompt_str: str):
        prompt = Prompt(prompt_str=prompt_str)
        if prompt.mark in self.prompts:
            self.prompts[prompt.mark].merge(prompt)
        else:
            self.prompts[prompt.mark] = prompt
        self.mark = prompt.mark

    def get_prompt(self) -> Prompt:
        return self.prompts[self.mark]
