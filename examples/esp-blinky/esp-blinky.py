import lobs


class EspBlinky(
    lobs.Package,
    version=lobs.Version(0, 0, 1),
    description="A simple ESP-IDF application project.",
):
    app = lobs.cpp.project.EmbeddedApplication(
        source_files=[lobs.Path(__file__).with_name("src") / "main.c"],
    )
