from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
import typing as t


V_T: t.TypeAlias = int | str | bool | float | Path
LV_T: t.TypeAlias = Iterable[V_T]


@dataclass
class Variable:
    name: str

    def to_reference(self) -> str:
        return "${" + self.name + "}"


@dataclass
class Project:
    name: str


@dataclass
class List:
    name: str
