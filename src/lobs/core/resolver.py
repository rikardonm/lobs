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


class PackageResolver:
    def __init__(self, root: type[Package], target: Path) -> None:
        self.root_klass = root
        self.target = target
        self.processed: dict[type[Package], Node] = {}
        self.tags_in_use: set[str] = set()

    def _reset(self) -> None:
        self.processed.clear()
        self.tags_in_use.clear()

    def recursively_resolve_package(self, klass: type[Package]) -> Node:
        tag_was_used = klass.tag in self.tags_in_use
        already_processed = klass in self.processed
        if tag_was_used and not already_processed:
            raise RuntimeError(f"Tag '{klass.tag}' is already in use by another package.")
        if already_processed:
            return self.processed[klass]

        current = klass()
        pkg_tgt = self.target / current.tag
        pkg_tgt.mkdir(parents=True, exist_ok=True)

        current.configure(None)
        current.prepare_files(pkg_tgt)
        project = current.materialize(pkg_tgt)

        node = Node(current, project, pkg_tgt)
        self.processed[klass] = node
        self.tags_in_use.add(klass.tag)

        for dep in project.get_dependencies():
            child_node = self.recursively_resolve_package(dep)
            node.append(child_node)

        return node

    def materialize_dag(self) -> Node:
        return self.recursively_resolve_package(self.root_klass)
