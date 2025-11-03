import functools
import typing as t
from pathlib import Path

import click

from lobs.core.package import base as pm
from lobs._machinery.modules import import_module
from lobs import exporters
from lobs.core.resolver import PackageResolver     # noqa: F401 register exporters

_T = t.TypeVar('_T')
_P = t.ParamSpec('_P')
_R = t.TypeVar('_R', covariant=True)


class _Base:
    _package_arg = click.argument(
        'package_path',
        required=True,
        type=click.Path(exists=False, file_okay=True, dir_okay=False, readable=True, path_type=Path),
    )
    _resolve_to = click.option(
        '--resolve-to',
        type=click.STRING,
        default=None,
        help="The directory name to resolve the packages to. If not provided, the packages are resolved in-place."
    )

    @classmethod
    def __package_builder(cls, package_path: Path) -> type[pm.Package]:
        print(f'Package: {package_path}')
        if not package_path.is_absolute():
            package_path = Path.cwd() / package_path
        else:
            package_path = package_path.absolute()
        if not package_path.exists():
            raise FileNotFoundError(f"Package file {package_path} does not exist.")
        project_package = pm.Package.capture_all_from_module(import_module('package_module', package_path))
        return project_package

    @classmethod
    def __resolve_to_builder(cls, resolve_to: Path | None) -> Path:
        if resolve_to is None:
            return Path.cwd() / 'lobs-project'
        resolve_path = Path(resolve_to)
        if not resolve_path.is_absolute():
            resolve_path = Path.cwd() / resolve_path
        return resolve_path

    class _UpstreamFunction(t.Protocol, t.Generic[_P, _R]):
        def __call__(self, package_path: Path, resolve_to: Path | None, *args: _P.args, **kwargs: _P.kwargs) -> _R:
            ...

    class _DownstreamFunction(t.Protocol, t.Generic[_P, _R]):
        def __call__(self, package: type[pm.Package], resolve_to: Path, *args: _P.args, **kwargs: _P.kwargs) -> _R:
            ...

    @classmethod
    def decorate(cls, func: _DownstreamFunction[_P, _R]) -> _UpstreamFunction[_P, _R]:
        func = cls._package_arg(func)
        func = cls._resolve_to(func)

        def _func(package_path: Path, resolve_to: Path | None, *args: _P.args, **kwargs: _P.kwargs) -> _R:
            package_klass = cls.__package_builder(package_path)
            resolve_to_path = cls.__resolve_to_builder(resolve_to)
            return func(package_klass, resolve_to_path, *args, **kwargs)

        functools.update_wrapper(_func, func)
        return _func


@click.group()
def main():
    """Lobs: A modern something system for C++ projects."""
    pass


@main.command()
@_Base.decorate
def materialize(package: type[pm.Package], resolve_to: Path):
    """Materialize the project package and its dependencies."""
    _ = PackageResolver(package, resolve_to).materialize_dag()


@main.command()
@_Base.decorate
def visualize(package: type[pm.Package], resolve_to: Path):
    """Visualize the project package and its dependencies as a DOT graph."""
    root = PackageResolver(package, resolve_to).materialize_dag()
    dag_dot = root.make_dag().to_dot()
    img_path = resolve_to / "dependency-graph.png"
    dag_dot.write_png(str(img_path))  # pyright: ignore
    print(f"Dependency graph written to: {img_path}")


@main.command()
@_Base.decorate
@click.argument(
    'exporter-tag',
    required=True,
    type=click.Choice(['cmake', 'espidf'], case_sensitive=False),
)
def export(package: type[pm.Package], resolve_to: Path, exporter_tag: str):
    """Export the projects to the desired build system format."""
    match exporter_tag.lower():
        case 'cmake':
            klass = exporters.cmake.Exporter
        case 'espidf':
            klass = exporters.esp_idf.Exporter
        case _:
            raise ValueError(f"Exporter with tag '{exporter_tag}' is not known.")

    root = PackageResolver(package, resolve_to).materialize_dag()
    exp = klass(root, resolve_to)
    exp.export()
