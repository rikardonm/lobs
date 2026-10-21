# SPDX-FileCopyrightText: 2025-present Ricardo Marchesan <rikardo.nm@proton.me>
#
# SPDX-License-Identifier: MIT
import dataclasses

from pydantic import BaseModel

from lobs.core.exporter import ExporterConfiguration as _BaseConfig
from lobs.core.exporter import GenericExporter
from lobs.core.resolver import Node


class Manifest(BaseModel):
    project: str
    version: str | None = None
    description: str | None = None
    type: str
    dependencies: list[str]


@dataclasses.dataclass
class ManifestConfig(_BaseConfig):
    indent: int = 2


class Exporter(GenericExporter[ManifestConfig]):
    def _export_node(self, node: Node, config: ManifestConfig) -> None:
        manifest = Manifest(
            project=node.package.tag,
            version=str(node.package.version) if node.package.version else None,
            description=node.package.description,
            type=type(node.project).__name__,
            dependencies=[dep.resolved_path.name for dep in node.children],
        )
        output_file = self.base_output_path / f"{node.package.tag}.json"
        output_file.write_text(manifest.model_dump_json(indent=config.indent), encoding="utf-8")
