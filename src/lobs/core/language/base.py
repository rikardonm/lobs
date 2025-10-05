from dataclasses import dataclass
import typing as t
from pathlib import Path


SOURCE: t.TypeAlias = Path | t.Generator[Path, None, None]


def _flatten_list(values: list[SOURCE]) -> list[Path]:
    ret: list[Path] = []
    for item in values:
        if isinstance(item, Path):
            ret.append(item)
        else:
            ret.extend(list(item))
    return ret


def expand_sources(files: list[SOURCE]) -> list[Path]:
    all_files = _flatten_list(files)
    if any(not pp.is_file() for pp in all_files):
        raise ValueError("Some source paths are not files.")
    return all_files


@dataclass
class Language:
    def __init_subclass__(cls, name: str) -> None:
        cls.name = name
