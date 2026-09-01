Getting Started with lobs
=========================

This guide will help you create your first ``lobs`` project from scratch. We'll cover:

1. Setting up a simple C++ application
2. Creating static libraries
3. Using external dependencies
4. Exporting to different build systems


Prerequisites
-------------

- Python 3.10 or later
- pip (Python package manager)
- An HTTP editor or IDE for writing Python code


Installation
------------

First, install ``lobs`` and its dependencies:

.. code-block:: console

   $ python -m pip install py-lobs


To develop with lobs, you can also clone the repository:

.. code-block:: console

   $ git clone https://github.com/ricardo/lobs.git
   $ cd lobs
   $ python -m pip install -e .[dev]


Project Structure
-----------------

A typical ``lobs`` project consists of:

.. code-block:: text

   myproject/
   ├── myproject.py            # Project definition file
   └── src/                    # Source files (for applications)
       └── main.cpp
   ├── include/                # Header files (for libraries)
       └── mylib.hpp


Creating Your First Project
---------------------------

Step 1: Create the Project File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a new file called ``hello.py`` with the following content:

.. literalinclude:: ../../examples/cmake-single-app/cmake-single-app.py
   :language: python
   :caption: hello.py - Your First lobs Project

This defines a simple C++ application project. The key components are:

- **Import statements**: Bring in ``lobs`` and necessary path utilities
- **Package class**: Inherits from ``lobs.Package`` to define your project
- **Project entity**: A ``SimpleManagedApplication`` that specifies the source file


Step 2: Run the Exporter
~~~~~~~~~~~~~~~~~~~~~~~~

Export your project to CMake format:

.. code-block:: console

   $ python hello.py export cmake

This creates a ``cmake-build/`` directory with a complete CMake configuration:

.. code-block:: text

   cmake-build/
   └── CMakeLists.txt


Step 3: Build and Run
~~~~~~~~~~~~~~~~~~~~~

Now build your application using standard CMake commands:

.. code-block:: console

   $ cd cmake-build
   $ cmake .
   $ cmake --build .
   $ ./hello

Expected output:

.. code-block:: text

   Hello from lobs!


Step 4: Explore the Generated Files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can inspect the generated CMakeLists.txt to see what was created:

.. code-block:: console

   $ cat cmake-build/CMakeLists.txt


Understanding Package Classes
-----------------------------

Every lobs project is defined by a subclass of :py:class:`lobus.Package`:

.. code-block:: python

   import lobs
   from pathlib import Path

   class MyProject(lobs.Package, version=lobs.Version(1, 0, 0)):
       """Your project description goes here."""

The class body defines:

- **Metadata**: ``version``, ``description``
- **Project entities**: Libraries, executables (as attributes)
- **Configuration**: Flags and settings applied to projects


Common Entity Types
-------------------

.. list-table:: Common Entity Types:
   :widths: 25 25 20
   :header-rows: 1

   * - Type
     - Use Case
     - Example
   * - SimpleManagedApplication
     - Standard executables
     - CLI tools, desktop apps
   * - SimpleLibrary
     - Static/shared libraries
     - Utility libraries
   * - EmbeddedApplication
     - Embedded targets (ESP-IDF)
     - IoT firmware


Customizing Your Project
------------------------

Modify Compilation Flags
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class MyProject(lobs.Package):
       app = lobs.cpp.project.SimpleManagedApplication(
           source_files=[Path("main.cpp")],
       )
       # Enable all warnings
       app.compilation_flags.w_all = True
       # Enable specific warning groups
       app.compilation_flags['w_extra'] = True


Setting C++ Standard
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   class MyCpp23Project(lobs.Package):
       lib = lobs.cpp.project.SimpleLibrary(
           source_files=[Path("lib.cpp")],
           cxx_standard=23,  # Use C++23 standard
       )


Adding Include Directories
~~~~~~~~~~~~~~~~~~~~~~~~~~

For libraries with public headers:

.. code-block:: python

   class MyLib(lobs.Package):
       lib = lobs.cpp.project.SimpleLibrary(
           source_files=[Path("lib.cpp")],
           public_includes=[Path(include)],  # Make headers available to consumers
       )


Creating Multi-Component Projects
---------------------------------

You can define multiple entities within a single package:

.. code-block:: python

   from pathlib import Path
   import lobs

   class ComposedApp(lobs.Package):
       """An application with its own library dependency."""

       # Define the utility library
       utils_lib = lobs.cpp.project.SimpleLibrary(
           source_files=[Path("src") / "utils.cpp"],
           public_includes=[Path(here) / include],
       )

       # Application that uses the library
       app = lobs.cpp.project.SimpleManagedApplication(
           source_files=[Path(src) / main.cpp],
           linked_libraries=[UtilsLib],  # Link to our utility library
       )


Command Line Usage
------------------

Exporters can be invoked from the command line:

.. code-block:: console

   $ python myproject.py export <exporter_name> [<options>]


Available Exporters:

- ``cmake`` - Generate CMake build files
- ``espidf`` - Generate ESP-IDF components


Example Workflow
----------------

Here's a complete workflow from project definition to running the application:

.. code-block:: console

   # 1. Define the project
   python myproject.py export cmake
   -- Project: hello-py

   # 2. Configure CMake
   cd cmake-build && cmake .
   -- Configuring done...

   # 3. Build
   cmake --build .
   -- Building... [100%]

   # 4. Run
   ./myapp
   Hello from lobs!


Troubleshooting
---------------

Common Issues and Solutions

No Source Files Found
~~~~~~~~~~~~~~~~~~~~~

Ensure your source file paths are correct:

.. code-block:: python

   app = lobs.cpp.project.SimpleManagedApplication(
       source_files=[Path(__file__).with_name("src") / "main.cpp"],  # Use Path.resolve() if needed
   )


Missing Dependencies
~~~~~~~~~~~~~~~~~~~~

When using external libraries, ensure they are installed:

.. code-block:: console

   $ python -m pip install nlohmann-json3-snapshot


Export Errors
~~~~~~~~~~~~~

Check that your project class is properly defined:

.. code-block:: text

   # Correct
   class MyApp(lobs.Package): ...

   # Incorrect (missing Package base class)
   class MyApp: ...


Next Steps
----------

Now that you understand the basics, explore:

- :doc:`architecture` - How lobs works internally
- :doc:`extensions` - Available exporters and creating custom ones
- :doc:`examples` - More advanced examples and use cases
- `API Reference` <api/index> - Complete class reference


See Also
--------

- :doc:`index` - Documentation overview
- :doc:`api/index` - Full API documentation
- `PyPI Package <https://pypi.org/project/py-lobs/>`_ - Latest releases
