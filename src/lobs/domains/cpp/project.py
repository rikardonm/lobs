import typing as t

import pydantic

from lobs.domains.files import SOURCES
from lobs.core.package.base import Project, Package
from lobs.domains.cpp.compiler_options import CompilationFlags


class SimpleEntity(Project):
    """This class represents a C++ library project."""
    public_includes: SOURCES = t.cast(SOURCES, pydantic.Field(default_factory=list))
    """List of include directories for the library."""
    source_files: SOURCES = t.cast(SOURCES, pydantic.Field(default_factory=list))
    """List of source files for the library."""
    private_includes: SOURCES = t.cast(SOURCES, pydantic.Field(default_factory=list))
    """List of private include directories for the library."""

    cxx_standard: int = 23
    """The C++ standard version to use for compiling the library."""
    compilation_flags: CompilationFlags = pydantic.Field(default_factory=CompilationFlags)
    """The compilation flags to use for compiling the application."""
    artifact_name: str | None = None
    """The name of the output library. If None, defaults to the project name."""
    linked_libraries: list[type[Package]] = t.cast(list[type[Package]], pydantic.Field(default_factory=list))
    """List of libraries to link against."""

    def get_dependencies(self) -> 'list[type[Package]]':
        return [lib for lib in self.linked_libraries]


class SimpleLibrary(SimpleEntity):
    pass


class SimpleManagedApplication(SimpleEntity):
    pass


class EmbeddedApplication(SimpleEntity):
    pass
