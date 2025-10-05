from dataclasses import dataclass

from lobs.core.language.base import expand_sources
from lobs.core.exporter import BaseExporter
from lobs.domains.cpp import project as cpp
import lobs.core.module as pm

from .cmake import CmakeFileWriter
from . import cmake_syntax as syntax
from ..core.configuration import ExporterConfiguration as _BaseConfig


@dataclass
class Config(_BaseConfig):
    ...


class Exporter(BaseExporter[Config], tag="esp-idf", config_cls=Config):
    def export(self) -> None:
        self._generate_component(self.module)

    def _generate_component(self, module: pm.ProjectModule) -> None:
        if not isinstance(module.pkg, cpp.Library):
            raise ValueError("The ESP-IDF exporter only supports C++ library projects.")

        all_files = expand_sources(module.pkg.source_files)

        writer = CmakeFileWriter(min_version="3.22")

        writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), module.pkg.cxx_standard)
        writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)

        # We expect a list of cpp files, but the IDF framework expects a list of directories
        # So we extract the least common directories from the source files
        src_dirs = writer.set(syntax.Variable("src_dirs"), {str(src.parent) for src in all_files})
        inc_dirs = writer.set(syntax.Variable("inc_dirs"), (str(x) for x in module.pkg.include_dirs))
        deps = writer.set(syntax.Variable("deps"), [d.name for d in module.pkg.meta.dependencies])

        writer.call(
            "idf_component_register",
            SRC_DIRS=src_dirs,
            INCLUDE_DIRS=inc_dirs,
            REQUIRES=deps,
        )

        # https://github.com/espressif/esp-idf/issues/7024
        outfile = module.filepath.parent / "CMakeLists.txt"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        writer.write_out(outfile)
