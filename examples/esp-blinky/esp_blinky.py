import lobs
import lobs.exporters

_cwd = lobs.Path(__file__).parent


class EspBlinky(lobs.Package):
    app = lobs.cpp.project.SimpleLibrary(
        source_files=[_cwd / "src" / "main.c"],
        linked_libraries=[],
    )

    def get_exporter_configuration(
        self, config_type: type[lobs.exporter.TCFG], gen_path: lobs.Path
    ) -> lobs.exporter.TCFG | None:
        if issubclass(config_type, lobs.exporters.esp_idf.EspIdfConfig):
            return config_type(
                esp_components=["driver"],
            )
        return None
