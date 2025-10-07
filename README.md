# lobs

[![PyPI - Version](https://img.shields.io/pypi/v/py-lobs.svg)](https://pypi.org/project/py-lobs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/py-lobs.svg)](https://pypi.org/project/py-lobs)

`lobs` is a framework that aims to provide an easy application and library project generator.


A simple C++ application example

```python
# simple-example.py
from pathlib import Path

import lobs


main_cpp = Path(__file__).with_name("main.cpp")

main_cpp.write_text(r"""
#include <iostream>

int main(int argc, char *argv[])
{
    (void)(argc);
    (void)(argv);
    std::cout << "Howdy!\n";
    return 0;
}
""")

app = lobs.Package(
    lobs.ProjectMeta("example-app", lobs.Version(0, 0, 1)),
    lobs.cpp.ManagedApplication([main_cpp]),
)
"""A simple C++ application project with a single source file,
no dependencies and default flags."""

# Example of modifying the project configuration after object creation
app.project.compilation_flags.w_all = True
# Example of enabling flags using dictionary-like access
app.project.compilation_flags['w_extra'] = True
# Example of adding a flag that was not predefined in the dataclass
app.project.compilation_flags['w_comment'] = True
```

And use it like so:

```
~/lobs » lobs simple-example.py export cmake
Project: simple-example.py

~/lobs » cmake -B build .
-- Configuring done
-- Generating done
-- Build files have been written to: /home/ricardo/git/lobs/build

~/lobs » cmake --build build
[ 50%] Building CXX object CMakeFiles/example-app.dir/main.cpp.o
[100%] Linking CXX executable example-app
[100%] Built target example-app

~/lobs » ./build/example-app
Howdy!
```


-----

## Table of Contents

- [Installation](#installation)
- [Design](#design)
- [Developer](#developer)
- [License](#license)

## Installation

```console
python3 -m pip install lobs
```

## Design

Various design choices were heavily based on the Zen of Python.


### All files exist in the disk

A limitation imposed by the framework to the Python language is that all executed code must be sourced from a file in disk.
The rationale is the commonuse of the module's path by the exporters.


### Explicit library imports in project files

The main reason for this is the reuse of editor and linting tools support.
Futhermore, it provides clarity to the user of what is being used and where it comes from.


### Everything is monkey-patchable

In standard Python, almost everything is monkey-patcheable by the user.
By design, the library aims to keep it that way.

> "C makes it easy to shoot yourself in the foot; C++ makes it harder, but when you do it blows your whole leg off".
> Yes, I said something like that (in 1986 or so).
> What people tend to miss, is that what I said there about C++ is to a varying extent true for all powerful languages.
> As you protect people from simple dangers, they get themselves into new and less obvious problems.
> Someone who avoids the simple problems may simply be heading for a not-so-simple one.
> One problem with very supporting and protective environments is that the hard problems may be discovered too late or be too hard to remedy once discovered.
> Also, a rare problem is harder to find than a frequent one because you don't suspect it.
>
> -- <cite>Bjarne Stroustrup @ https://www.stroustrup.com/quotes.html</cite>


## Developer

TODO

## License

`lobs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
