import dataclasses

from lobs.domains.files import SOURCES
from lobs.core.package.base import Project, Package
from lobs.domains.cpp.compiler_options import CompilationFlags


@dataclasses.dataclass
class SimpleEntity(Project):
    """This class represents a C++ library project."""
    public_includes: SOURCES = dataclasses.field(default_factory=list)  # type: ignore
    """List of include directories for the library."""
    source_files: SOURCES = dataclasses.field(default_factory=list)  # type: ignore
    """List of source files for the library."""
    private_includes: SOURCES = dataclasses.field(default_factory=list)  # type: ignore
    """List of private include directories for the library."""

    cxx_standard: int = 23
    """The C++ standard version to use for compiling the library."""
    compilation_flags: CompilationFlags = dataclasses.field(default_factory=CompilationFlags)
    """The compilation flags to use for compiling the application."""
    artifact_name: str | None = None
    """The name of the output library. If None, defaults to the project name."""
    linked_libraries: list[type[Package]] = dataclasses.field(default_factory=list)  # type: ignore
    """List of libraries to link against."""

    def _get_dependencies(self):
        return self.linked_libraries


class SimpleLibrary(SimpleEntity):
    pass


class SimpleManagedApplication(SimpleEntity):
    pass


class EmbeddedApplication(SimpleEntity):
    pass
