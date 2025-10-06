from pathlib import Path

import lobs


_tf = Path(__file__)


app = lobs.Package(
    lobs.ProjectMeta(_tf.stem, lobs.Version.parse(lobs.__version__)),
    lobs.cpp.ManagedApplication([_tf.with_name("src") / "main.cpp"]),
)
"""A simple C++ application project with a single source file, no dependencies and default flags."""

# Example of modifying the project configuration after object creation
app.project.compilation_flags.w_all = True
# Example of enabling flags using dictionary-like access
app.project.compilation_flags['w_extra'] = True
# Example of adding a flag that was not predefined in the dataclass
app.project.compilation_flags['w_comment'] = True
