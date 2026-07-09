import dataclasses
import typing as t

from lobs.core.package.base import Project, Package
from lobs.core.exporter import GenericExporter, ExporterConfiguration as _BaseConfig
from lobs.core.resolver import Node
from lobs.domains.cpp import project as cpp

from . import syntax
from .writer import CmakeFileWriter


@dataclasses.dataclass
class CmakeBasedProject(Project):
    """A (usually) imported C++ project is natively based on CMake."""
    dependencies: list[type[Package]] = dataclasses.field(default_factory=list)  # type: ignore

    def _get_dependencies(self) -> t.Sequence[Package]:
        return self.dependencies


@dataclasses.dataclass
class CmakeConfig(_BaseConfig):
    minimum_cmake_version: str = "3.22"


class Exporter(GenericExporter[CmakeConfig]):
    _resolved_packages: dict[Node, syntax.Library] = {}

    def _export_node(self, node: Node, config: CmakeConfig) -> None:
        prj = node.project
        match prj:
            case cpp.SimpleManagedApplication():
                writer = self._export_entity(node, prj)
                # the application gets the top-level CMakeLists.txt
                writer.write_to_dir(self.base_output_path)
            case cpp.SimpleLibrary():
                writer = self._export_entity(node, prj)
                writer.write_to_dir(node.resolved_path)
            case _:
                raise ValueError(f"The CMake exporter only supports C++ projects, got {type(prj)}.")

    @classmethod
    def resolve_app_name(cls, app: cpp.SimpleManagedApplication | cpp.SimpleLibrary, node: Node) -> str:
        return app.artifact_name or node.package.tag

    def _export_entity(
        self,
        node: Node,
        app: cpp.SimpleManagedApplication | cpp.SimpleLibrary | CmakeBasedProject,
    ) -> CmakeFileWriter:
        writer = CmakeFileWriter(min_version=self._config.minimum_cmake_version)
        opt_args: dict[str, t.Any] = {}

        if node.package.description:
            opt_args["DESCRIPTION"] = node.package.description

        prj = writer.make_project(
            name=node.package.tag,
            version=str(node.package.version) if node.package.version else None,
            languages=["CXX"],
            **opt_args,
        )

        with writer.group():
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD"), app.cxx_standard)
            writer.set(syntax.Variable("CMAKE_CXX_STANDARD_REQUIRED"), True)

        match (app):
            case cpp.SimpleManagedApplication():
                exe = writer.add_executable(self.resolve_app_name(app, node), app)
                for dep in node.children:
                    writer.add_subdirectory(dep.resolved_path.relative_to(self.base_output_path))
                    writer.target_link_library(exe, self._resolved_packages[dep])
            case cpp.SimpleLibrary():
                lib = writer.add_library(self.resolve_app_name(app, node), app)
                self._resolved_packages[node] = lib
                for dep in node.children:
                    # writer.add_subdirectory(dep.resolved_path)
                    writer.target_link_library(lib, self._resolved_packages[dep])
            case CmakeBasedProject():
                raise NotImplementedError()
            case _:
                raise ValueError(
                    f"The CMake exporter does not support the selected target {type(app)} on '{node.name}'."
                )

        enabled_flags: list[str] = []
        for t_, f in app.compilation_flags.get_split():
            match t_:
                case "w":
                    enabled_flags.append(f"-W{f}")
                case "f":
                    enabled_flags.append(f"-f{f}")
                case _:
                    raise ValueError(f"Unable to convert flag {f} of type {t_}")

        if enabled_flags:
            writer.call(
                "target_compile_options",
                prj.name,
                "PRIVATE",
                enabled_flags,
            )

        return writer
