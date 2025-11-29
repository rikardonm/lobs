"""Helper definitions for NVS memory layout."""
import typing as t
from pathlib import Path

from filesizelib import Storage


class Entry(t.NamedTuple):
    name: str
    type: str
    subtype: str
    start: Storage
    size: Storage
    flags: list[str] = []

    @property
    def end(self) -> Storage:
        return self.start + self.size


class Table:
    def __init__(self, *entries: Entry, offset: int | None = None) -> None:
        self.entries = entries
        self.offset = offset

    def export(self, output_file: Path) -> None:
        entries: list[tuple[str, str, str, str, str, str]] = []
        entries.append(('# Name',  'Type', 'SubType', 'Offset', 'Size', 'Flags'))
        for entry in self.entries:
            flags_str = ",".join(entry.flags) if entry.flags else ""
            start = entry.start.KIB.decimal_value
            size = entry.size.KIB.decimal_value
            if start.as_integer_ratio()[1] != 1:
                raise ValueError(f"Start offset for entry '{entry.name}' is not aligned to KiB.")
            if size.as_integer_ratio()[1] != 1:
                raise ValueError(f"Size for entry '{entry.name}' is not aligned to KiB.")
            entries.append((entry.name, entry.type, entry.subtype, f"{int(start)}k", f"{int(size)}k", flags_str))

        column_widths = [max(len(row[i]) for row in entries) for i in range(len(entries[0]))]

        with output_file.open("w", encoding="utf-8") as f:
            f.write("# NVS Partition Table\n")
            for row in entries:
                line = ", ".join(row[i].ljust(column_widths[i]) for i in range(len(row)))
                f.write(line + "\n")
