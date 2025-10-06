import dataclasses
import typing as t

from lobs.core.language.base import SOURCES
from lobs.core.project import Project
from lobs.domains.cpp.compiler_options import CompilationFlags


@dataclasses.dataclass
class ManagedApplication(Project):
    """This class represents an application that is managed by an underlying system (e.g. Linux, Windows, macOS)."""
    source_files: SOURCES
    """List of source files for the application."""
    include_dirs: SOURCES = t.cast(SOURCES, dataclasses.field(default_factory=list))
    """List of include directories for the library."""
    cxx_standard: int = 23
    """The C++ standard version to use for compiling the application."""
    compilation_flags: CompilationFlags = dataclasses.field(default_factory=CompilationFlags)
    """The compilation flags to use for compiling the application."""
    executable_name: str | None = None
    """The name of the output executable. If None, defaults to the project name."""


@dataclasses.dataclass
class Library(Project):
    """This class represents a C++ library project."""
    include_dirs: SOURCES = t.cast(SOURCES, dataclasses.field(default_factory=list))
    """List of include directories for the library."""
    source_files: SOURCES = t.cast(SOURCES, dataclasses.field(default_factory=list))
    """List of source files for the library."""
    cxx_standard: int = 23
    """The C++ standard version to use for compiling the library."""
    compilation_flags: CompilationFlags = dataclasses.field(default_factory=CompilationFlags)
    """The compilation flags to use for compiling the application."""
