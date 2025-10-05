import typing as t
from pathlib import Path
import shutil

import click

from lobs.core import exporter
from lobs._machinery.modules import import_module
from lobs.core import module as pm
from lobs import exporter as _     # noqa: F401 register exporters


@click.group()
@click.argument(
    'project_path',
    required=False,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path),
)
@click.pass_context
def main(ctx: click.Context, project_path: Path | None = None):
    ctx.ensure_object(dict)
    print(f'Project: {project_path}')
    if project_path is None:
        cwd = Path.cwd()
        project_path = cwd / cwd.parent.with_suffix('.py').stem
    if not project_path.is_absolute():
        project_path = Path.cwd() / project_path
    else:
        project_path = project_path.absolute()
    if not project_path.exists():
        raise FileNotFoundError(f"Project file {project_path} does not exist.")
    module = pm.ProjectModule.from_module(
        import_module('project_module', project_path),
        filepath=project_path,
    )
    ctx.obj['lobs-package'] = module


@main.command()
@click.argument(
    'exporter-tag',
    required=True,
    type=click.Choice(list(exporter.IExporter.KNOWN.keys()), case_sensitive=False),
)
@click.option(
    '--clean',
    is_flag=True,
    help="Clean the build directory before exporting."
)
@click.pass_context
def export(ctx: click.Context, exporter_tag: str, clean: bool):
    module = t.cast(pm.ProjectModule, ctx.obj['lobs-package'])

    if clean and module.filepath.exists():
        shutil.rmtree(module.filepath)

    klass = exporter.IExporter.KNOWN[exporter_tag]
    _exp = klass(module)
    _exp.export()
