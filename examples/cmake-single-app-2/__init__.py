import lobs


class CMakeSingleApp2Example(
    lobs.Package,
    version=lobs.Version(0, 0, 1),
    description="A simple C++ application project using CMake.",
):
    app = lobs.cpp.project.SimpleManagedApplication(
        source_files=[lobs.Path(__file__).with_name("src") / "main.cpp"],
    )
