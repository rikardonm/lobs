"""

Issues to watch out for:
    - https://github.com/espressif/esp-idf/issues/7024
"""
from collections.abc import Sequence
from pathlib import Path
import re
from dataclasses import dataclass

import lobs.core.project as p
from lobs.core.configuration import ExporterConfiguration as _BaseConfig
from lobs.core.exporter import BaseExporter
from lobs.core.language.base import expand_sources
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


class Exporter(BaseExporter[EspIdfConfig], tag="esp-idf", config_cls=EspIdfConfig):
    CMAKE_MIN_VERSION = "3.22"

    def export(self) -> None:
        meta = self.package.meta
        prj = self.package.project
        match prj:
            case cpp.ManagedApplication():
                # Resolve this package and all its dependencies
                self._generate_application(meta, prj)
                for d in self.package.dependencies:
                    Exporter(d).export()
            case cpp.Library():
                writer = self._generate_component(prj, [d.meta.name for d in self.package.dependencies])
                writer.write_to_dir(self.project_folder)
            case _:
                raise ValueError(f"The ESP-IDF exporter does not support the selected target {prj}.")

    def _generate_application(self, meta: p.ProjectMeta, app: cpp.ManagedApplication) -> None:
        # In case of esp-idf applications, there is an expected project tree structure.
        # Namely, there are no source files in the same directory as the root CMakeLists.txt
        # Instead, all source files are delegated into components, taking special note of the `main` component.
        # See: https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-guides/build-system.html#example-project  # noqa: E501
        #
        # So, we therefore expect:
        #   - The `main` directory is a direct child of the project root
        #   - All listed source files are in the `main` subdirectory
        sources = expand_sources(app.source_files)
        main_dir = self.project_folder / "main"
        if not main_dir.exists():
            raise FileNotFoundError(f"The expected 'main' directory does not exist at {main_dir}.")
        if not all(x.is_relative_to(main_dir) for x in sources):
            raise ValueError(f"All source files must be located in the 'main' directory at {main_dir}.")

        main_writer = self._generate_component(
            cpp.Library(
                source_files=sources,
                include_dirs=app.include_dirs,
                cxx_standard=app.cxx_standard,
                compilation_flags=app.compilation_flags,
            ),
            [d.meta.name for d in self.package.dependencies] + list(self.config.required_components or []),
        )
        main_writer.write_to_dir(main_dir)

        # Now we generate the root CMakeLists.txt
        writer = CmakeFileWriter(min_version=self.CMAKE_MIN_VERSION)
        writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)

        if all_deps_paths := self.package.collect_dependencies_paths():
            all_deps_paths.discard(self.package.package_path)
            if missing := [str(p) for p in all_deps_paths if not p.exists()]:
                raise FileNotFoundError(f"The following dependency paths do not exist: {', '.join(missing)}")
            writer.list("EXTRA_COMPONENT_DIRS").append(*all_deps_paths)

        if self.config.sdk_config_default is not None:
            sdkconfig_path = Path(self.config.sdk_config_default)
            if not sdkconfig_path.is_absolute():
                sdkconfig_path = Path.cwd() / sdkconfig_path
            if not sdkconfig_path.exists():
                raise FileNotFoundError(f"The specified sdkconfig.default file does not exist at {sdkconfig_path}.")
            writer.list("SDKCONFIG_DEFAULTS").append(
                "${CMAKE_CURRENT_LIST_DIR}/"
                + str(sdkconfig_path.relative_to(self.project_folder))
            )

        writer.variable("COMPONENTS").set(["main"])

        with writer.group():
            writer.include("$ENV{IDF_PATH}/tools/cmake/project.cmake")
            writer.call("project", meta.name)

        writer.write_to_dir(self.project_folder)

    @classmethod
    def _generate_component(cls, lib: cpp.Library, dependencies: Sequence[str]) -> CmakeFileWriter:
        all_files = expand_sources(lib.source_files)
        writer = CmakeFileWriter(min_version=cls.CMAKE_MIN_VERSION)

        # We expect a list of cpp files, but the IDF framework expects a list of directories
        # So we extract the least common directories from the source files
        src_dirs = writer.set(syntax.Variable("src_dirs"), {str(src.parent) for src in all_files})
        inc_dirs = writer.set(syntax.Variable("inc_dirs"), (str(x) for x in lib.include_dirs))
        deps = writer.set(syntax.Variable("deps"), dependencies)

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
