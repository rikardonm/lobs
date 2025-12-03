"""

Issues to watch out for:
    - https://github.com/espressif/esp-idf/issues/7024
"""
import dataclasses
import re
import typing as t
from collections.abc import Sequence
from pathlib import Path

from lobs.core.exporter import ExporterConfiguration as _BaseConfig
from lobs.core.exporter import GenericExporter
from lobs.core.resolver import Node
from lobs.domains.cpp import project as cpp
from lobs.domains.files import expand_sources
from lobs.exporters.cmake import syntax as syntax
from lobs.exporters.cmake.writer import CmakeFileWriter

from . import sdkconfig


@dataclasses.dataclass
class EspIdfConfig(_BaseConfig):
    esp_components: Sequence[str] = ()
    """List of ESP-IDF components to include in the project."""
    config_flags: sdkconfig.FT = t.cast(sdkconfig.FT, dataclasses.field(default_factory=dict))
    """List of configuration flags required for the project."""


class Exporter(GenericExporter[EspIdfConfig]):
    CMAKE_MIN_VERSION = "3.22"

    def _merge_config_flags(self, config: EspIdfConfig) -> None:
        """Merge de node's configuration flags into the top-level configuration."""
        conflicts = set(config.config_flags).intersection(self._config.config_flags)
        if conflicts:
            raise ValueError(f"Conflicting configuration flags found: {', '.join(conflicts)}")
        self._config.config_flags.update(config.config_flags)

    def _export_node(self, node: Node, config: EspIdfConfig) -> None:
        # get the configuration options for the project
        #   - fetch the resolved flags/values
        #   - fetch the current exporter configuration
        match node.project:
            case cpp.EmbeddedApplication():
                self._generate_application(node, node.project, config, self.base_output_path)
                # the application gets the top-level CMakeLists.txt
                # app_writer.write_to_dir(self.base_output_path)

            case cpp.SimpleLibrary():
                self._merge_config_flags(config)
                self._generate_component(node, node.project, config, node.resolved_path)
            case _:
                raise ValueError(
                    f"The ESP-IDF exporter does not support the selected target {node.project} on '{node.name}'."
                )

    @classmethod
    def resolve_app_name(cls, app: cpp.EmbeddedApplication | cpp.SimpleLibrary, node: Node) -> str:
        return app.artifact_name or node.package.tag

    def _generate_application(
        self,
        node: Node,
        app: cpp.EmbeddedApplication,
        config: EspIdfConfig,
        output_file_path: Path,
    ) -> None:
        writer = CmakeFileWriter(min_version=self.CMAKE_MIN_VERSION)

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)
            # see: https://docs.espressif.com/projects/esp-idf/en/release-v5.5/esp32/api-guides/build-system.html#searching-for-components  # noqa: E501
            # this means we can directly "link" to the components' directory (and not their parents)
            if all_deps_paths := {x.resolved_path for x in self._flat_node_list}:
                all_deps_paths.discard(node.resolved_path)
                if missing := [str(p) for p in all_deps_paths if not p.exists()]:
                    raise FileNotFoundError(f"The following dependency paths do not exist: {', '.join(missing)}")
                if all_deps_paths:
                    writer.list("EXTRA_COMPONENT_DIRS").append(*all_deps_paths)

            if self._config.config_flags:
                sdk_cfg_path = output_file_path / "sdkconfig.defaults"
                sdkconfig.generate_file(self._config.config_flags, sdk_cfg_path)
                if not sdk_cfg_path.is_absolute():
                    sdk_cfg_path = Path.cwd() / sdk_cfg_path
                if not sdk_cfg_path.exists():
                    raise FileNotFoundError(f"The specified sdkconfig.defaults file does not exist at {sdk_cfg_path}.")
                writer.list("SDKCONFIG_DEFAULTS").append(str(sdk_cfg_path))

            writer.variable("COMPONENTS").set([x.name for x in node.children] + list(config.esp_components))

        with writer.group():
            writer.include("$ENV{IDF_PATH}/tools/cmake/project.cmake")
            writer.call("project", self.resolve_app_name(app, node))

        writer.write_to_dir(output_file_path)

    def _generate_component(
        self,
        node: Node,
        lib: cpp.SimpleLibrary | cpp.EmbeddedApplication,
        config: EspIdfConfig,
        output_file_path: Path,
    ) -> None:
        all_files = expand_sources(lib.source_files)
        writer = CmakeFileWriter(min_version=self.CMAKE_MIN_VERSION)

        # We expect a list of cpp files, but the IDF framework expects a list of directories
        # So we extract the least common directories from the source files
        src_dirs = writer.set(syntax.Variable("src_dirs"), {str(src.parent) for src in all_files})
        inc_dirs = writer.set(syntax.Variable("inc_dirs"), (str(x) for x in lib.public_includes))
        deps = writer.set(syntax.Variable("deps"), [x.name for x in node.children] + list(config.esp_components))

        writer.call(
            "idf_component_register",
            SRC_DIRS=src_dirs,
            INCLUDE_DIRS=inc_dirs,
            REQUIRES=deps,
        )

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), lib.cxx_standard)
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)

        enabled_flags = [field.name for field in lib.compilation_flags.get_all() if lib.compilation_flags[field.name]]

        if enabled_flags:
            writer.call(
                "target_compile_options",
                syntax.Variable("COMPONENT_LIB"),
                "PRIVATE",
                *(re.sub(r"^w_", "-W", x).replace("_", "-") for x in enabled_flags),
            )

        writer.write_to_dir(output_file_path)
