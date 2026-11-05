"""This module resolves the package dependencies and converts package providers into `ResolvedPackage` instances."""

from pathlib import Path
import typing as t

from bigtree import DAGNode as _Node, DAG as _DAG  # pyright: ignore[reportPrivateImportUsage]
import pydot

from lobs.core.package.base import Package, Project


class Node(_Node):
    def __init__(
        self,
        package: Package,
        project: Project,
        resolved_path: Path,
        **kwargs: t.Any,
    ) -> None:
        super().__init__(name=package.tag, **kwargs)
        self.package = package
        self.project = project
        self.resolved_path = resolved_path

    def make_dag(self) -> "DAG":
        return DAG(self)


class DAG(_DAG):
    def __init__(self, root: Node) -> None:
        super().__init__(root)

    def to_dot(self) -> pydot.Dot:
        # return self.to_dot(node_attr="node_style")
        return super().to_dot()  # type: ignore
