Welcome to lobs!
================

lobs is a Python framework that simplifies application and library project generation 
for embedded and general-purpose C++ projects. It provides a unified approach to 
create build configurations that work seamlessly with multiple build systems (CMake, ESP-IDF, Zephyr, etc.).

The core philosophy is inspired by the **Zen of Python**: simple, explicit, and practical solutions to real-world problems.

What Problem Does lobs Solve?
-----------------------------

Embedded applications declared in plain CMake do not play well with ESP-IDF, 
and vice-versa. Instead of writing conditional logic everywhere or wrapping complexity 
in obscure layers, lobs puts that abstraction where you can see and control it: 
in a clean Python file.

The core motivation is solving the pain of maintaining parallel project definitions for different build systems. 
With lobs, you write **one** project definition in Python, and export it to your target build system as needed.


Key Principles
--------------

- **Every library is a package**::
    
    Each unit of functionality is encapsulated as a Package subclass.

- **Every application is a plain script**::
    
    Project definitions are simple Python files that import from lobs.

- **Dependency resolution via pip**::
    
    Use Python's package manager (pip) for dependency fetching and version resolution.

- **One package, one target**::
    
    Each package contains exactly one library or application.


Features
--------

* **Simple Project Definitions** - Write project definitions in readable Python without complex build system DSLs
* **Multiple Export Targets** - Generate CMake, ESP-IDF, or other configurations from the same source
* **Dependency Management** - Automatic dependency fetching using Python's native package ecosystem
* **Explicit Control** - Full visibility and control over generated build configurations


Quick Example
-------------

Here is a minimal example of a C++ application using lobs:

.. code-block:: python

   # simple-example.py

   from pathlib import Path
   import lobs

   main_cpp = Path(__file__).with_name("main.cpp")

   main_cpp.write_text("""
#include <iostream>

int main(int argc, char *argv[])
{
    (void)(argc);
    (void)(argv);
    std::cout << "Hello from lobs!" << endl;
    return 0;
}
""")

   # Define the package with its project entity
   app = lobs.Package(
       lobs.ProjectMeta("simple-example", lobs.Version(0, 1, 0)),
       lobs.cpp.project.SimpleManagedApplication([main_cpp]),
   )


Export to CMake and Build:

.. code-block:: console

   $ # Export the project as CMake
   $ python simple-example.py export cmake
   Project: simple-example.py

   $ # Configure and build with cmake
   $ cmake -B build .
   -- Configuring done
   -- Generating done
   
   $ cmake --build build


Output:

.. code-block:: console

   Hello from lobs!


Installation
------------

The package is available on PyPI:

.. code-block:: console

   $ python -m pip install py-lobs

Or install from source:

.. code-block:: console

   $ git clone https://github.com/ricardo/lobs.git
   $ cd lobs
   $ python -m pip install -e .


Getting Help
------------

- `GitHub Repository <https://github.com/ricardo/lobs>`_  
- `PyPI Page <https://pypi.org/project/py-lobs/>`_  
- `API Reference <api/index.html>`_  


Documentation Structure
-----------------------

**Core Sections:**

.. toctree::
   :maxdepth: 2

   getting_started
   architecture
   extensions
   examples


**Reference Material:**

.. toctree::
   :maxdepth: 2
   
   api/index
