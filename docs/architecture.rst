Architecture
============

This document describes the overall architecture and core building blocks of ``lobs``.


.. _architecture-overview:

Overview
--------

The framework follows a multi-phase workflow to generate build configurations from Python project definitions.

**Workflow Diagram**

The workflow proceeds through consecutive phases: ::

    Start [Create] Configure PrepareFiles => Materialize ==> Exporter [CMake.IDF]

Each phase feeds into the next, culminating in build system output.

The flow consists of the following phases:

#. **Create**: The skeleton for the declared entity (application, library) is created.
#. **Configure**: Dependencies are recursively resolved and satisfied.
#. **Prepare Files**: All required files are prepared and paths are finalized.
#. **Materialize**: Project files are generated to disk or made available.
#. **Export**: Specific build system configurations are generated.


.. _build:

Building Blocks
---------------

``lobs`` is organized around several key abstractions:

- **Package** - The fundamental unit that encapsulates a project entity
- **Project** - Represents the actual buildable entity (executable, library)  
- **Exporter** - Translates project definitions into specific build system configurations


The Package
~~~~~~~~~~~

At the core of ``lobs`` is the :class:`lobs.core.package.base.Package` class, which serves as both a container and a registry for project definitions.

.. code-block:: python

   from lobs import Package

   class MyProject(Package):
       version = Version(0, 1, 0)
       description = "My custom project"

       # Define the project entity below
       app: SimpleManagedApplication | None = None

Key features:

- **Subclass Registry**: Every ``Package`` subclass is automatically registered by tag name
- **Metadata**: Each package carries version, description, and optional tags
- **Dependency Resolution**: Packages can declare requirements via :py:class:`lobs.core.package.base.Parameter`


.. autoclass:: lobs.core.package.base.Package
   :members:
   :show-inheritance:
   :no-index:

The Project Class
~~~~~~~~~~~~~~~~~

Projects represent the actual buildable entity (executable, static library, interface library, etc.). They are defined within domains such as C++.

**C++ Domains in ``lobs``:**

+-------------------------+----------------------------------------------------------+
| Entity Type             | Description                                              |
+=========================+==========================================================+
| SimpleEntity            | Base class for all C++ entities with configurable        |
|                         | build options                                            |
+-------------------------+----------------------------------------------------------+
| SimpleLibrary           | Static or interface library target                       |
+-------------------------+----------------------------------------------------------+
| SimpleManagedApplication| Executable application target                            |
+-------------------------+----------------------------------------------------------+
| EmbeddedApplication     | Specialized for embedded targets (e.g., ESP-IDF)         |
+-------------------------+----------------------------------------------------------+


Example Project Definition

.. code-block:: python

   class MyProject(Package, description="My library"):
       # Define a C++ static library
       lib = lobs.cpp.project.SimpleLibrary(
           source_files=[Path(__file__).with_name("src") / "lib.cpp"],
           public_includes=[Path(__file__).with_name("include")],
           cxx_standard=23,
           compilation_flags={
               'w_all': True,
               'w_extra': False,
           }
       )

.. autoclass:: lobs.domains.cpp.project.SimpleEntity
   :members:
   :no-index:


The C++ Domain
~~~~~~~~~~~~~~

The ``lobs.cpp`` domain provides abstractions for C++ build entities.

**Source Files Handling**

.. code-block:: python

   from pathlib import Path
   import lobs

   source_files = [
       Path(__file__).with_name("src") / "main.cpp",
       Path(__file__).with_name("src") / "utils.cpp",
   ]


**Compilation Flags**

The :py:class:`lobs.domains.cpp.compiler_options.CompilationFlags` dataclass provides structured access to compiler warning flags:

.. code-block:: python

   flags = CompilationFlags(
       w_all=True,
       w_extra=True,
       w_pedantic=True,
       w_error=False,
   )

Add custom flags dynamically:

.. code-block:: python

   flags["w_new_custom_flag"] = True  # Will be converted to -W-new-custom-flag


**Entity Options**

All C++ entities share common configuration options:

- **source_files**: List of source files (.cpp, .c)
- **public_includes**: Public include directories
- **private_includes**: Private include directories (for libraries only)
- **cxx_standard**: C++ standard version (default: 23 for C++23)
- **compilation_flags**: Compile-time flag configuration
- **artifact_name**: Override for output target name


The Exporter Pattern
~~~~~~~~~~~~~~~~~~~~

Exporters translate project definitions into specific build system configurations.


Exporter Architecture

.. code-block:: python

   from lobs.core.exporter import GenericExporter, ExporterConfiguration

   class MyExporter(GenericExporter[MyConfig]):

       def _export_node(self, node: Node, config: MyConfig) -> None:
           """Generate export-specific configuration."""
           prj = node.project
           # Apply export logic based on project type


Key exporter methods:

.. autoclass:: lobs.core.exporter.GenericExporter
   :members:
   :undoc-members:
   :show-inheritance:
   :no-index:

Exporter Configuration

Exporters accept configuration objects to customize output:

.. code-block:: python

   @dataclasses.dataclass
   class CmakeConfig(lobs exporters.ExporterConfiguration):
       minimum_cmake_version: str = "3.22"


Resolving Dependencies
----------------------

Package dependencies are automatically resolved through Python's type system and validation library.

**Requirement Syntax**

.. code-block:: python

   import annotated_types as ant

   class Consumer(Package):
       dependency_param = Parameter[str](default=None)

       def __init__(self, *args, **kwargs):
           super().__init__(*args, **kwargs)
           # Add requirements during initialization
           self.dependency_param.require(
               DependencyProvider,
               ant.Gt(5),  # Require value > 5
           )


**Validation Examples**

+-------------------+-------------------------------+--------------------------------------------------+
| Constraint        | Description                   | Example                                          |
+===================+===============================+==================================================+
| Ant.Gt(N)         | Greater than N                | "version": ant.Gt(2)                             |
+-------------------+-------------------------------+--------------------------------------------------+
| Ant.Lt(N)         | Less than N                   | "count": ant.Lt(100)                             |
+-------------------+-------------------------------+--------------------------------------------------+
| Predicate(func)   | Custom function check         | "name": ant.Predicate(str.isupper)               |
+-------------------+-------------------------------+--------------------------------------------------+

Dependency Resolution Flow

::

   +---------------------+        +----------------+        +-----------------+
   | Consumer Package    | -----> | Declare        | ---->  | Add Requirements|
   +---------------------+        +----------------+        +-----------------+
                                                |
                                                v
   +---------------------+        +----------------+        +------------------+
   | Validate Constraints| <----  | Resolve        | <----  | Find Providers   |
   +---------------------+        +----------------+        +------------------+

   
File Generation Flow
--------------------

Files are materialized through a systematic process:

1. **Path Resolution**: All file paths are resolved relative to the project base directory
2. **Directory Creation**: Necessary parent directories are created automatically
3. **Content Generation**: Configuration files (CMakeLists.txt, etc.) are generated
4. **Copy/Move Resources**: Source files and assets are copied if needed

.. code-block:: python

   from pathlib import Path

   # The generator will handle this automatically
   class MyProject(Package):
       def _prepare_files(self, basepath: Path) -> None:
           # Custom file preparation logic
           manifest = basepath / "manifest.json"
           manifest.write_text("{}", encoding='utf-8')


The Write Phase
~~~~~~~~~~~~~~~

When exporting to a build system, the write phase generates all build files in the target directory structure. For CMake:

.. code-block:: text

   export/
   ├── CMakeLists.txt          # Root CMake configuration
   ├── MyLibrary/
   │   └── CMakeLists.txt      # Library CMake configuration
   └── MyApp/
       └── CMakeLists.txt      # Application CMake configuration


Source files remain in their original locations; only configuration files are generated.


See Also
--------

- :doc:`extensions`: Available exporters and how to extend them
- :doc:`api/index`: Complete API reference
- :doc:`examples`: Working examples with complete project definitions
