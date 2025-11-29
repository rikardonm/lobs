from collections.abc import Sequence
import typing as t
from pathlib import Path


SOURCE_GEN: t.TypeAlias = t.Generator[Path, None, None]
SOURCES: t.TypeAlias = Sequence[Path | SOURCE_GEN] | SOURCE_GEN | t.Iterator[Path]


def _flatten_list(values: SOURCES) -> list[Path]:
    ret: list[Path] = []
    for item in values:
        if isinstance(item, Path):
            ret.append(item)
        else:
            ret.extend(list(item))
    return ret


def expand_sources(files: SOURCES) -> list[Path]:
    all_files = _flatten_list(files)
    not_files = list(filter(lambda p: not p.is_file(), all_files))
    if any(not_files):
        raise ValueError(f"Some source paths are not files: {not_files}")
    return all_files
