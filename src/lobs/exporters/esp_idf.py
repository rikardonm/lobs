"""

Issues to watch out for:
    - https://github.com/espressif/esp-idf/issues/7024
"""
from collections.abc import Sequence
from pathlib import Path
import re
from dataclasses import dataclass

from lobs.core.configuration import ExporterConfiguration as _BaseConfig
from lobs.core.exporter import BaseExporter
from lobs.core.resolver import Node
from lobs.domains.files import expand_sources
from lobs.domains.cpp import project as cpp

from .cmake import syntax as syntax
from .cmake.writer import CmakeFileWriter


@dataclass
class EspIdfConfig(_BaseConfig):
    required_components: Sequence[str] | None = None
    """List of ESP-IDF components required by the project (in addition to package dependencies)."""
    sdk_config_default: Path | None = None
    """Path to a sdkconfig.default file to use as the default configuration for the project.
    If not specified, no default configuration will be used."""


class Exporter(BaseExporter):
    CMAKE_MIN_VERSION = "3.22"

    def export(self) -> None:
        self._config = EspIdfConfig()
        super().export()

    def _export_node(self, node: Node) -> None:
        prj = node.project
        match prj:
            case cpp.EmbeddedApplication():
                comp_writer = self._generate_component(node, prj)
                comp_writer.write_to_dir(node.resolved_path)
                app_writer = self._generate_application(node, prj)
                # the application gets the top-level CMakeLists.txt
                app_writer.write_to_dir(self.base_output_path)

            case cpp.SimpleLibrary():
                comp_writer = self._generate_component(node, prj)
                comp_writer.write_to_dir(node.resolved_path)
            case _:
                raise ValueError(f"The ESP-IDF exporter does not support the selected target {prj}.")

    @classmethod
    def resolve_app_name(cls, app: cpp.EmbeddedApplication | cpp.SimpleLibrary, node: Node) -> str:
        return app.artifact_name or node.package.tag

    def _generate_application(self, node: Node, app: cpp.EmbeddedApplication) -> CmakeFileWriter:
        writer = CmakeFileWriter(min_version=self.CMAKE_MIN_VERSION)

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)
            if all_deps_paths := {x.resolved_path.parent for x in self._flat_node_list}:
                all_deps_paths.discard(node.resolved_path.parent)
                if missing := [str(p) for p in all_deps_paths if not p.exists()]:
                    raise FileNotFoundError(f"The following dependency paths do not exist: {', '.join(missing)}")
                if all_deps_paths:
                    writer.list("EXTRA_COMPONENT_DIRS").append(*all_deps_paths)

            if self._config.sdk_config_default is not None:
                sdkconfig_path = Path(self._config.sdk_config_default)
                if not sdkconfig_path.is_absolute():
                    sdkconfig_path = Path.cwd() / sdkconfig_path
                if not sdkconfig_path.exists():
                    raise FileNotFoundError(f"The specified sdkconfig.default file does not exist at {sdkconfig_path}.")
                writer.list("SDKCONFIG_DEFAULTS").append(
                    "${CMAKE_CURRENT_LIST_DIR}/"
                    + str(sdkconfig_path.relative_to(node.resolved_path))
                )

            writer.variable("COMPONENTS").set([node.name])

        with writer.group():
            writer.include("$ENV{IDF_PATH}/tools/cmake/project.cmake")
            writer.call("project", self.resolve_app_name(app, node))

        return writer

    def _generate_component(self, node: Node, lib: cpp.SimpleLibrary | cpp.EmbeddedApplication) -> CmakeFileWriter:
        all_files = expand_sources(lib.source_files)
        writer = CmakeFileWriter(min_version=self.CMAKE_MIN_VERSION)

        # We expect a list of cpp files, but the IDF framework expects a list of directories
        # So we extract the least common directories from the source files
        src_dirs = writer.set(syntax.Variable("src_dirs"), {str(src.parent) for src in all_files})
        inc_dirs = writer.set(syntax.Variable("inc_dirs"), (str(x) for x in lib.public_includes))
        deps = writer.set(syntax.Variable("deps"), [x.name for x in node.children])

        writer.call(
            "idf_component_register",
            SRC_DIRS=src_dirs,
            INCLUDE_DIRS=inc_dirs,
            REQUIRES=deps,
        )

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), lib.cxx_standard)
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)

        enabled_flags = [
            field.name
            for field in lib.compilation_flags.get_all()
            if lib.compilation_flags[field.name]
        ]

        if enabled_flags:
            writer.call(
                "target_compile_options",
                syntax.Variable("COMPONENT_LIB"),
                'PRIVATE',
                *(re.sub(r'^w_', '-W', x).replace('_', '-') for x in enabled_flags),
            )

        return writer
