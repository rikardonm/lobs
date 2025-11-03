import contextlib
from dataclasses import dataclass
import typing as t
from pathlib import Path

from lobs.domains import cpp

from . import syntax


class CmakeFileWriter:
    INDENT = "    "
    MAX_ARG_LEN = 20

    def _should_export_single_line(self, args: list[str]) -> bool:
        return len(args) <= 3 and not any(len(x) > self.MAX_ARG_LEN for x in args)

    def __init__(self, min_version: str):
        self.cnt: list[str] = []
        self._write_newline = True
        self.call("cmake_minimum_required", VERSION=min_version)

    def __newline(self) -> None:
        if self._write_newline:
            self.cnt.append("")

    def write_to_dir(self, outdir: Path) -> Path:
        outfile = outdir / "CMakeLists.txt"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        # Ensure the file ends with a newline
        nl = "\n" if self.cnt and self.cnt[-1] != "" else ""
        outfile.write_text("\n".join(self.cnt) + nl)
        return outfile

    @contextlib.contextmanager
    def group(self):
        """Suppress newlines after each statement within the context."""
        self._write_newline = False
        yield
        self._write_newline = True
        if not self.cnt[-1] == "":
            self.__newline()

    def set(self, var: syntax.Variable, value: syntax.V_T | syntax.LV_T | None) -> syntax.Variable:
        if value is None:
            self.cnt.append(f"unset({var.name})")
            self.__newline()
        elif isinstance(value, (bool, int, str, float, Path)):
            self.cnt.append(f"set({var.name} {self.resolve_value(value)})")
            self.__newline()
        else:
            values = list(self.resolve_value(v) for v in value)
            if not values:
                self.set(var, None)
            elif self._should_export_single_line(values):
                self.set(var, " ".join(values))
            else:
                self.cnt.append(f"set({var.name}")
                self.cnt.extend(f"{self.INDENT}{v}" for v in values)
                self.cnt.append(")")
                self.__newline()
        return var

    @classmethod
    def resolve_value(cls, v: syntax.V_T | syntax.LV_T | None | syntax.Variable) -> str:
        if isinstance(v, syntax.Variable):
            return v.to_reference()
        if v is None:
            return ""
        if isinstance(v, bool):
            return "ON" if v else "OFF"
        if isinstance(v, (int, str, float)):
            return str(v)
        if isinstance(v, Path):
            return str(v)
        return " ".join(str(x) for x in v)

    def _escape_argument(self, arg: syntax.VTT) -> syntax.VTT:
        if isinstance(arg, str):
            if " " in arg or '"' in arg or "'" in arg or "(" in arg or ")" in arg:
                return f'"{arg.replace("\"", "\\\"")}"'
        return arg

    def make_project(
        self,
        name: str,
        version: str | None = None,
        languages: list[str] | None = None,
        **kwargs: syntax.V_T | syntax.LV_T | None | syntax.Variable,
    ) -> syntax.Project:
        opt_args: dict[str, t.Any] = {}
        if version is not None:
            opt_args["VERSION"] = version
        if languages is not None:
            opt_args["LANGUAGES"] = " ".join(languages)
        opt_args.update(kwargs)
        prj = syntax.Project(name=name)
        opt_args = {k: self._escape_argument(v) for k, v in opt_args.items() if v is not None}
        self.call("project", prj.name, **opt_args)
        return prj

    def add_executable(self, name: str, app: cpp.project.SimpleManagedApplication) -> syntax.Executable:
        exe = syntax.Executable(name=name)
        assert app.source_files, "An executable must have at least one source file."
        self.call("add_executable", exe.name, *(str(x) for x in app.source_files))
        return exe

    def add_library(self, name: str, lib: cpp.project.SimpleLibrary) -> syntax.Library:
        library = syntax.Library(name=name)
        if lib.source_files:
            self.call("add_library", library.name, "STATIC", *(str(x) for x in lib.source_files))
            if lib.public_includes:
                self.call(
                    "target_include_directories",
                    library.name,
                    "PUBLIC",
                    *(str(x) for x in lib.public_includes),
                )
            if lib.private_includes:
                self.call(
                    "target_include_directories",
                    library.name,
                    "PRIVATE",
                    *(str(x) for x in lib.private_includes),
                )
        else:
            self.call("add_library", library.name, "INTERFACE")
            if lib.public_includes:
                self.call(
                    "target_include_directories",
                    library.name,
                    "INTERFACE",
                    *(str(x) for x in lib.public_includes),
                )
            if lib.private_includes:
                raise RuntimeError("An interface library cannot have private includes.")
        return library

    def add_subdirectory(
        self,
        source_dir: Path,
    ) -> None:
        self.call("add_subdirectory", str(source_dir))

    def target_link_library(self, exe: syntax.Executable | syntax.Library, lib: syntax.Library) -> None:
        self.call("target_link_libraries", exe.name, lib.name)

    def call(
        self,
        name: str,
        *args: syntax.V_T | syntax.LV_T | syntax.Variable,
        **kwargs: syntax.V_T | syntax.LV_T | None | syntax.Variable,
    ) -> None:
        _args = [self.resolve_value(x) for x in args]
        _kwargs = [f"{k} {self.resolve_value(v)}" for k, v in kwargs.items()]
        resolved_args = _args + _kwargs
        if self._should_export_single_line(resolved_args):
            self.cnt.append(f"{name}(" + " ".join(resolved_args) + ")")
        else:
            self.cnt.append(f"{name}(")
            self.cnt.extend((self.INDENT + x for x in resolved_args))
            self.cnt.append(")")
        self.__newline()

    def variable(self, name: str) -> "_Variable":
        return _Variable(_writer=self, _var=syntax.Variable(name=name))

    def list(self, name: str) -> "_List":
        return _List(_writer=self, _var=syntax.Variable(name=name))

    def include(self, filepath: Path | str) -> None:
        self.call("include", str(filepath))


@dataclass
class _Variable:
    _writer: CmakeFileWriter
    _var: syntax.Variable

    @property
    def name(self) -> str:
        return self._var.name

    def set(self, value: syntax.V_T | syntax.LV_T | None) -> None:
        self._writer.set(self._var, value)


@dataclass
class _List:
    _writer: CmakeFileWriter
    _var: syntax.Variable

    @property
    def name(self) -> str:
        return self._var.name

    def append(self, *value: syntax.V_T | syntax.LV_T) -> None:
        """Append a value or a list of values to the list."""
        self._writer.call("list", "APPEND", self.name, *value)
