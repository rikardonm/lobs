import dataclasses
from importlib import metadata
from pathlib import Path
import re
import typing as t

from lobs.core.language.base import expand_sources
from lobs.core.exporter import BaseExporter
from lobs.domains.cpp import project as cpp
import lobs.core.module as pm
import lobs.core.project as p

from . import cmake_syntax as syntax
from ..core.configuration import ExporterConfiguration as _BaseConfig


class CmakeFileWriter:
    INDENT = '    '
    MAX_ARG_LEN = 12

    def _should_export_single_line(self, args: list[str]) -> bool:
        return len(args) < 3 and not any(len(x) > self.MAX_ARG_LEN for x in args)

    def __init__(self, min_version: str):
        self.cnt: list[str] = []
        self.call("cmake_minimum_required", VERSION=min_version)

    def write_out(self, file: Path) -> None:
        file.write_text('\n'.join(self.cnt))

    def set(self, var: syntax.Variable, value: syntax.V_T | syntax.LV_T | None) -> syntax.Variable:
        if value is None:
            self.cnt.append(f"unset({var.name})")
        elif value is True:
            self.cnt.append(f"set({var.name} ON)")
        elif value is False:
            self.cnt.append(f"set({var.name} OFF)")
        elif isinstance(value, (int, str, float)):
            self.cnt.append(f"set({var.name} {value})")
        else:
            values = list(self._resolve_value(v) for v in value)
            if not values:
                self.cnt.append(f"unset({var.name})")
            elif self._should_export_single_line(values):
                self.cnt.append(f"set({var.name} {' '.join(str(v) for v in values)})")
            else:
                self.cnt.append(f"set({var.name}")
                self.cnt.extend(f"{self.INDENT}{v}" for v in values)
                self.cnt.append(")")
        self.cnt.append("")
        return var

    def _resolve_value(self, v: syntax.V_T | syntax.LV_T | None | syntax.Variable) -> str:
        if isinstance(v, syntax.Variable):
            return v.to_reference()
        if v is None:
            return ""
        if isinstance(v, bool):
            return "ON" if v else "OFF"
        if isinstance(v, (int, str, float)):
            return str(v)
        return ' '.join(str(x) for x in v)

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
            opt_args["LANGUAGES"] = ' '.join(languages)
        opt_args.update(kwargs)
        self.call("project", name, **opt_args)
        return syntax.Project(name=name)

    def call(
        self,
        name: str,
        *args: syntax.V_T | syntax.LV_T | syntax.Variable,
        **kwargs: syntax.V_T | syntax.LV_T | None | syntax.Variable,
    ) -> None:
        _args = [self._resolve_value(x) for x in args]
        _kwargs = [f"{k} {self._resolve_value(v)}" for k, v in kwargs.items()]
        resolved_args = _args + _kwargs
        if self._should_export_single_line(resolved_args):
            self.cnt.append(f'{name}(' + ' '.join(resolved_args) + ')')
        else:
            self.cnt.append(f"{name}(")
            self.cnt.extend((self.INDENT + x for x in resolved_args))
            self.cnt.append(")")
        self.cnt.append("")


@dataclasses.dataclass
class Config(_BaseConfig):
    minimum_cmake_version: str = "3.22"


class Exporter(BaseExporter[Config], tag="cmake", config_cls=Config):
    def export(self) -> None:
        match self.module.pkg.project:
            case cpp.ManagedApplication():
                writer = self._export_application(self.module.pkg.meta, self.module.pkg.project)
            case cpp.Library():
                writer = self._export_library(self.module.pkg.meta, self.module.pkg.project)
            case _:
                raise ValueError("The CMake exporter only supports C++ projects.")

        outfile = self.module.filepath.parent / "CMakeLists.txt"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        writer.write_out(outfile)

    def _export_application(self, meta: p.ProjectMeta,  app: cpp.ManagedApplication) -> CmakeFileWriter:
        writer = CmakeFileWriter(min_version=self.config.minimum_cmake_version)
        opt_args: dict[str, t.Any] = {}

        if meta.short_description:
            opt_args["DESCRIPTION"] = meta.short_description

        prj = writer.make_project(
            name=meta.name,
            version=str(meta.version),
            languages=["CXX"],
            **opt_args,
        )
        writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)
        writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)
        writer.call("add_executable", prj.name, str(app.entrypoint))

        enabled_flags = [
            field.name
            for field in app.compilation_flags.get_all()
            if app.compilation_flags[field.name]
        ]

        if enabled_flags:
            writer.call(
                "target_compile_options",
                prj.name,
                'PRIVATE',
                *(re.sub(r'^w_', '-W', x).replace('_', '-') for x in enabled_flags),
            )

        return writer

    def _export_library(self, meta: p.ProjectMeta, module: cpp.Library) -> CmakeFileWriter:
        raise NotImplementedError()
