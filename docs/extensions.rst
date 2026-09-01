Extensions and Exporters
========================

This document describes the built-in exporters and how to extend ``lobs`` with new export formats.


Available Exporters
-------------------

``lobe`` includes exporters for popular build systems. New exporters can be easily added by subclassing :py:class:`lobus.exporter.GenericExporter`.


.. index::
   single: cmake exporter


CMake Exporter
~~~~~~~~~~~~~~

The CMake exporter generates standard CMake project files for C++ targets.

**Features:**

- Automatic generation of ``CMakeLists.txt`` files
- Support for executable and library targets
- Link dependencies between projects
- Customizable C++ standard and compilation flags


**Usage**

.. code-block:: console

   # Export a project to CMake from the command line
   python myproject.py export cmake

Or use programmatically:

.. code-block:: python

   from pathlib import Path
   import lobs

   class MyProject(Package):
       app = lobs.cpp.project.SimpleManagedApplication(
           source_files=[Path(__file__).with_name("main.cpp")],
       )

   # Export to CMake directory
   Path("./myproject").mkdir(exist_ok=True)
   app.exporters.cmake(Path("./myproject")).run()


**Generated Output**

The exporter produces the following files:

.. code-block:: cmake

   # Root CMakeLists.txt
   cmake_minimum_required(VERSION 3.22)
   project(myproject VERSION 0.1 LANGUAGES CXX)

   set(CMAKE_CXX_STANDARD 23)
   set(CMAKE_CXX_STANDARD_REQUIRED ON)

   add_subdirectory(libs/mylib)
   add_executable(myapp main.cpp)

   target_link_libraries(myapp PRIVATE mylib)

   target_compile_options(myapp PRIVATE -Wall -Wextra -pedantic)


**Configuration Options**

The CMake exporter accepts the following configuration:

.. code-block:: python

   @dataclass
   class CmakeConfig(ExporterConfiguration):
       minimum_cmake_version: str = "3.22"  # Default minimum CMake version

Pass configuration when running:

.. code-block:: python

   export_config = CmakeConfig(minimum_cmake_version="3.20")
   app.exporters.cmake(Path("./myproject"), config=export_config).run()


Compilation Flags Support
~~~~~~~~~~~~~~~~~~~~~~~~~

The exporter automatically detects enabled compilation flags and translates them to compiler options:

.. code-block:: python

   class MyProject(Package):
       app = lobs.cpp.project.SimpleManagedApplication(
           source_files=[Path(__file__).with_name("main.cpp")],
       )
       # Enable warning flags
       app.compilation_flags.w_all = True
       app.compilation_flags['w_pedantic'] = True


The exporter will generate:

.. code-block:: cmake

   target_compile_options(myapp PRIVATE -Wall -Wpedantic)


.. index::
   single: esp-idf; exporter


ESP-IDF Exporter
~~~~~~~~~~~~~~~~

The ESP-IDF exporter generates configuration suitable for Espressif's IoT Development Framework.

**Features:**

- ESP-IDF component structure generation
- NVS (Non-Volatile Storage) partition handling
- sdkconfig integration support


**Usage**

.. code-block:: console

   # Export a project to ESP-IDF format
   python myespapp.py export espidf

Or programmatically:

.. code-block:: python

   import lobs
   from pathlib import Path

   class EspBlinky(Package):
       app = lobs.cpp.project.EmbeddedApplication(
           source_files=[Path(__file__).with_name("src") / "main.c"],
       )

   # Export to ESP-IDF directory structure
   exporter = app.exporters.espidf(Path("./esp-project"))
   exporter.run()


**Generated Output**

The ESP-IDF exporter creates a component-based structure:

.. code-block:: text

   esp-project/
   ├── CMakeLists.txt              # Project root configuration
   ├── sdkconfig                   # ESP-IDF configuration
   ├── myapp/                      # Component directory
   │   ├── CMakeLists.txt          # Component CMake config
   │   └── main.c                  # Entry point source


Component Configuration

Each component includes its own ``CMakeLists.txt`` with proper ESP-IDF integration:

.. code-block:: cmake

   idf_component_register(
       SRCS "main.c"
       INCLUDE_DIRS "."
   )

NVS Partition Support
~~~~~~~~~~~~~~~~~~~~~

The ESP-IDF exporter provides built-in support for NVS partition tables:

.. code-block:: python

   # Create an application with NVS configuration
   class EspressifApp(Package):
       app = lobs.cpp.project.EmbeddedApplication(
           source_files=[Path(__file__).with_name("main.c")],
           nvs_partition=lobs.exporters.esp_idf.NVSPartitionEntry(
               namespace="storage",
               size_hint=32*1024,  # 32KB
           )
       )

SDKConfig Helper

.. autoclass:: lobs.exporters.esp_idf.sdkconfig
   :members:


Creating Custom Exporters
-------------------------

You can create custom exporters by extending :py:class:`lobs.core.exporter.GenericExporter`.


Exporter Base Template

Here is a minimal exporter template:

.. code-block:: python

   from dataclasses import dataclass
   from pathlib import Path

   from lobs.core.exporter import GenericExporter, ExporterConfiguration
   from lobs.core.resolver import Node

   @dataclass
   class MyCustomConfig(ExporterConfiguration):
       """Configuration options for custom exporter."""
       output_format: str = "json"

   class CustomExporter(GenericExporter[MyCustomConfig]):
       """Custom exporter example."""

       def _export_node(self, node: Node, config: MyCustomConfig) -> None:
           """Export a single node to the target format."""
           project = node.project

           # Handle different project types
           match project:
               case lobs.cpp.project.SimpleManagedApplication():
                   self._export_application(node, project, config)
               case lobs.cpp.project.SimpleLibrary():
                   self._export_library(node, project, config)
               case _:
                   raise ValueError(f"Unsupported project type: {type(project)}")

       def _export_application(self, node: Node, app, config: MyCustomConfig) -> None:
           """Export application project."""

           if config.output_format == "json":
               self._export_json(node, app, config)

       def _export_library(self, node: Node, lib, config: MyCustomConfig) -> None:
           """Export library project."""
           # Your implementation here
           pass

       def _write_to_file(self, content: str, filename: Path) -> None:
           """Helper to write content to file."""
           filename.parent.mkdir(parents=True, exist_ok=True)
           filename.write_text(content, encoding='utf-8')


Registering Exporter Command-Line Interface

To use your custom exporter from the command line:

.. code-block:: bash

   # Add your exporter module to PYTHONPATH or install package
   python myproject.py export custom


Example Custom Configuration Writer

Here's an example that generates a JSON manifest:

.. code-block:: python

   import json
   from pathlib import Path
   from dataclasses import dataclass, asdict

   from lobs.core.exporter import GenericExporter, ExporterConfiguration


   @dataclass
   class ManifestConfig(ExporterConfiguration):
       """JSON manifest exporter configuration."""
       indent: int = 2


   class ManifestExporter(GenericExporter[ManifestConfig]):
       """Export project definitions as JSON manifests."""

       def _export_node(self, node: Node, config: ManifestConfig) -> None:
           manifest_data = {
               "project": node.package.tag,
               "version": str(node.package.version),
               "description": node.package.description,
               "type": type(node.project).__name__,
               "dependencies": [
                   dep.resolved_path.name for dep in node.children
               ],
           }

           output_file = self.base_output_path / f"{node.package.tag}.json"
           output_file.write_text(
               json.dumps(manifest_data, indent=config.indent),
               encoding='utf-8'
           )


Best Practices for Custom Exporters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Handle all project types**: Ensure your exporter knows how to handle SimpleLibrary, SimpleManagedApplication, etc.

2. **Use path resolution**: Always use ``node.resolved_path`` and ``self.base_output_path`` for paths.

3. **Pass configuration through**: Respects the :py:class:`MyCustomConfig` parameters passed from the user.

4. **Validate inputs**: Check that projects are valid before attempting export.

5. **Provide meaningful errors**: Use descriptive error messages when encountering unsupported configurations.


See Also
--------

- :doc:`extensions`: Architecture details on project generation
- :py:class:`lobus.exporters.ExporterConfiguration` base class reference
- :pep:`501`: For information on Python packaging standards used for dependency resolution
