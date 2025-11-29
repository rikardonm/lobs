from lobs import Package, cpp, Path


class LibA(
    Package,
    description="A sample configurable library.",
):
    app = cpp.project.SimpleLibrary(
        source_files=[Path(__file__).parent / "lib_a" / "lib_a.cpp"],
        public_includes=[Path(__file__).parent / "lib_a"],
    )
