import lobs


class CMakeSingleAppExample(
    lobs.Package,
    version=lobs.Version(0, 0, 1),
    description="A simple C++ application project using CMake.",
):
    app = lobs.cpp.project.SimpleManagedApplication(
        source_files=[lobs.Path(__file__).with_name("src") / "main.cpp"],
    )

    # Example of modifying the project configuration after object creation
    app.compilation_flags.w_all = True
    # Example of enabling flags using dictionary-like access
    app.compilation_flags["w_extra"] = True
    # Example of adding a flag that was not predefined
    app.compilation_flags["w_comment"] = True
