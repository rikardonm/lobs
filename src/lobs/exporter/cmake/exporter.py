import dataclasses
import re
import typing as t

import lobs.core.project as p
from lobs.core.exporter import BaseExporter
from lobs.domains.cpp import project as cpp

from lobs.core.configuration import ExporterConfiguration as _BaseConfig
from . import syntax
from . writer import CmakeFileWriter


@dataclasses.dataclass
class CmakeConfig(_BaseConfig):
    minimum_cmake_version: str = "3.22"


class Exporter(BaseExporter[CmakeConfig], tag="cmake", config_cls=CmakeConfig):
    def export(self) -> None:
        meta = self.package.meta
        prj = self.package.project
        match prj:
            case cpp.ManagedApplication():
                writer = self._export_application(meta, prj, self.config)
            case cpp.Library():
                writer = self._export_library(meta, prj)
            case _:
                raise ValueError("The CMake exporter only supports C++ projects.")

        writer.write_to_dir(self.project_folder)

    @classmethod
    def _export_application(
        cls,
        meta: p.ProjectMeta,
        app: cpp.ManagedApplication,
        config: CmakeConfig,
    ) -> CmakeFileWriter:
        writer = CmakeFileWriter(min_version=config.minimum_cmake_version)
        opt_args: dict[str, t.Any] = {}

        if meta.short_description:
            opt_args["DESCRIPTION"] = meta.short_description

        prj = writer.make_project(
            name=meta.name,
            version=str(meta.version),
            languages=["CXX"],
            **opt_args,
        )

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)

        writer.call("add_executable", prj.name, *(str(x) for x in app.source_files))

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
