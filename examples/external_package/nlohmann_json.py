from lobs import (
    Package,
    cpp,
    Path,
    providers,
    Version,
)


class NlohmannJsonPackage(
    Package,
    version=Version(3, 12, 0),
    tag="nlohmann_json",
):
    def _prepare_files(self, basepath: Path):
        _provider = providers.DownloadablePackage(
            f"https://github.com/nlohmann/json/releases/download/v{self.version}/json.tar.xz"
        )
        _provider.resolve_to(basepath)

    def _make_project(self, basepath: Path):
        return cpp.project.SimpleLibrary(
            public_includes=[basepath / "json" / "single_include"],
            source_files=[],
            private_includes=[],
            artifact_name="nlohmann_json",
        )
