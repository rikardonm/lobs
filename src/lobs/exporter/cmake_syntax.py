from collections.abc import Iterable
from dataclasses import dataclass
import typing as t


V_T: t.TypeAlias = int | str | bool | float
LV_T: t.TypeAlias = Iterable[V_T]


@dataclass
class Variable:
    name: str

    def to_reference(self) -> str:
        return "${" + self.name + "}"


@dataclass
class Project:
    name: str
