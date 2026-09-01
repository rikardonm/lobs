API Reference
=============

Complete API reference for ``lobs`` modules and classes.


.. index::
   single: api; overview

For detailed source code documentation, see the actual source files in the repository.


Core Package Module
-------------------

The core package module provides fundamental building blocks for project definitions.

Package
~~~~~~~

.. automodule:: lobs.core.package.base
   :members:
   :undoc-members:
   :show-inheritance:


Version Module
--------------

Provides semantic versioning support for package metadata.

.. automodule:: lobs.core.version
   :members:
   :undoc-members:
   :show-inheritance:


Resolver Module
---------------

Handles dependency resolution and graph management.

.. automodule:: lobs.core.resolver
   :members:
   :undoc-members:
   :show-inheritance:


Exporter Module
---------------

Base functionality for generating build system configurations.

.. automodule:: lobs.core.exporter
   :members:
   :undoc-members:
   :show-inheritance:


CMake Exporter Module
---------------------

CMake configuration generation.

.. automodule:: lobs.exporters.cmake
   :members:
   :undoc-members:
   :synopsis: CMake build system exporter for lobs projects
   :show-inheritance:
   :no-index:


C++ Domain Module
-----------------

C++ project entity definitions.

.. automodule:: lobs.domains.cpp.project
   :members:
   :undoc-members:
   :show-inheritance:


C++ Compiler Options Module
---------------------------

Management of compilation flags for C++ projects.

.. automodule:: lobs.domains.cpp.compiler_options
   :members:
   :undoc-members:
   :show-inheritance:


ESP-IDF Exporter Module
-----------------------

ESP-IDF target configuration support.

.. automodule:: lobs.exporters.esp_idf
   :members:
   :undoc-members:
   :synopsis: ESP-IDF component exporter for lobs projects
   :show-inheritance:


Utilities Module
----------------

Logger and module utilities.

.. automodule:: lobs.machinery.logger
   :members:
   :undoc-members:
   :show-inheritance:


Files Domain Module
-------------------

Source file management utilities.

.. automodule:: lobs.domains.files
   :members:
   :undoc-members:
   :show-inheritance:

SOURCES Type Alias
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   SOURCES = list[Path]  # type alias for source file paths


Module Structure Summary
------------------------

Here is a summary of the core modules and their purposes:

**Core Package (:py:meth:`lobs.core.package.base`)**
    Fundamental building blocks - :py:class:`~lobs.core.package.base.Package`,
    :py:class:`~lobs.core.package.base.Project`, :py:class:`~lobs.core.package.base.Parameter`

**Version Management (:py:meth:`lobus.core.version`)**
    Semantic versioning with :py:class:`~lobs.core.version.Version`

**Dependency Resolver (:py:meth:`lobs.core.resolver`)**
    Graph-based resolution for project dependencies

**Exporters (:py:meth:`lobs.exporters`).**: Generate build configurations
    - :py:class:`~lobus.exporters.cmake.Exporter` - CMake configuration generation
    - :py:class:`~lobs.exporters.esp_idf.Exporter` - ESP-IDF component export

**Domain Definitions (:py:meth:`lobs.domains.cpp.project`)**
    - :py:class:`~lobs.domains.cpp.project.SimpleLibrary` - Static/shared libraries
    - :py:class:`~lobus.domains.cpp.project.SimpleManagedApplication` - Executable apps
    - :py:class:`~lobs.domains.cpp.project.EmbeddedApplication` - Embedded targets

**Compiler Options (:py:meth:`lobs.domains.cpp.compiler_options`)**
    Type-safe warning flag management via :py:class:`~lobs.domains.cpp.compiler_options.CompilationFlags`


Cross-References
----------------

.. py:function:: Package(tag, description)

   Create a new package instance for project definitions.
   
   See also: :doc:`../getting_started`

.. py:class:: Version(major, minor, patch=0)

   Semantic version class with comparison operators.

.. py:class:: CompilationFlags
    """Dataclass for C++ compilation flags."""

.. method:: CompilationFlags.__setitem__(key, value)

   Set a flag value by key (e.g., ``w_all = True``).


Index and Search
----------------

For quick reference:

.. glossary::

   Package
       A Python class that inherits from :py:class:`lobus.Package` to define a project unit.
   
   Project
       The buildable entity (application, library) inside a package.
   
   Exporter
       A translator that generates build system files (CMake, ESP-IDF).
