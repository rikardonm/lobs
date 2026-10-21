import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from lobs.core.package.base import Package
from lobs.machinery.modules import import_module
from lobs.core.resolver import PackageResolver
from lobs.domains.cpp.project import SimpleManagedApplication
from lobs.exporters.cmake.exporter import Exporter as CMakeExporter
from lobs.exporters.manifest import Exporter as ManifestExporter, Manifest

from ._config import examples_dir


class ManifestTestPackage(Package, tag="ManifestExporterTestPackage"):
    app = SimpleManagedApplication()


__ref_dot_simple = """strict digraph G {
rankdir=TB;
}
"""


__ref_dot_external = """strict digraph G {
rankdir=TB;
nlohmann_json [label="nlohmann_json"];
ExternalPackageExample [label=ExternalPackageExample];
ExternalPackageExample -> nlohmann_json;
LibA [label=LibA];
ExternalPackageExample [label=ExternalPackageExample];
ExternalPackageExample -> LibA;
}
"""


@pytest.mark.parametrize(
    "test_file,ref_dot",
    [
        (["cmake-single-app", "cmake-single-app.py"], __ref_dot_simple),
        (["external_package", "external_package.py"], __ref_dot_external),
    ],
    ids=["simple", "external"],
)
def test_export_library(
    test_file: list[str],
    ref_dot: str,
):
    target_file = examples_dir.joinpath(*test_file)
    with tempfile.TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)
        output_path = tmpdir / "lobs-project"

        package_klass = Package.capture_all_from_module(import_module('project_module', target_file))

        # 2 - materialize every package
        resolver = PackageResolver(package_klass, output_path)
        root = resolver.materialize_dag()
        dag_dot = root.make_dag().to_dot()
        assert dag_dot.to_string() == ref_dot

        # 3 - do stuff with it, like export
        # we don't really check anything here, but just that we can run it
        exp = CMakeExporter(root, output_path)
        exp.export()


@pytest.mark.parametrize(
    "test_file",
    [
        (["cmake-single-app", "cmake-single-app.py"]),
        (["external_package", "external_package.py"]),
    ],
    ids=["simple", "external"],
)
def test_export_cli(test_file: list[str]):
    # runner = click.testing.CliRunner()
    target_file = examples_dir.joinpath(*test_file)
    with tempfile.TemporaryDirectory() as _tmpdir:
        tmpdir = Path(_tmpdir)
        output_path = tmpdir / "lobs-project"

        # We can't use the click runner because it messes with our "smart" stateful classes
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "lobs",
                "export",
                str(target_file),
                "--resolve-to",
                str(output_path),
                "cmake",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr


def test_export_manifest():
    with tempfile.TemporaryDirectory() as _tmpdir:
        output_path = Path(_tmpdir) / "lobs-project"
        root = PackageResolver(ManifestTestPackage, output_path).materialize_dag()

        ManifestExporter(root, output_path).export()

        manifest_file = output_path / f"{root.package.tag}.json"
        manifest = Manifest.model_validate_json(manifest_file.read_text(encoding="utf-8"))
        assert manifest.project == root.package.tag
        assert manifest.version is None
        assert manifest.type == type(root.project).__name__
        assert manifest.dependencies == []


def test_export_manifest_cli():
    target_file = examples_dir / "cmake-single-app" / "cmake-single-app.py"
    with tempfile.TemporaryDirectory() as _tmpdir:
        output_path = Path(_tmpdir) / "lobs-project"
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from lobs.__main__ import main; main()",
                "export",
                str(target_file),
                "--resolve-to",
                str(output_path),
                "manifest",
            ],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert (output_path / "CMakeSingleAppExample.json").is_file()
