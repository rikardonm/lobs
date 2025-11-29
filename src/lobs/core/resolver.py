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
        self.root = root
        self.target = target
        self.processed: dict[type[Package], tuple[Package, Node]] = {}

    def _reset(self) -> None:
        self.processed.clear()

    def recursively_resolve_package(self, current: type[Package]) -> tuple[Node, set[type[Package]], list[Exception]]:
        print(f'Resolving package: {current.__module__}.{current.__qualname__}...')
        unresolved: set[type[Package]] = set()
        captured_exceptions: list[Exception] = []
        if x := self.processed.get(current, None):
            # So we mutate the package configuration when we encounter it again
            # in a sort of "running" merge fashion.
            # x[0]._intake_configuration(current)
            return (x[1], unresolved, captured_exceptions)

        pkg_tgt = self.target / current.tag
        pkg_tgt.mkdir(parents=True, exist_ok=True)

        inst = current()

        inst._prepare_files(pkg_tgt)  # pyright: ignore[reportPrivateUsage]
        inst._validate_configuration()  # pyright: ignore[reportPrivateUsage]
        project = inst._make_project(pkg_tgt)  # pyright: ignore[reportPrivateUsage]

        node = Node(inst, project, pkg_tgt)
        self.processed[current] = (inst, node)
        for dep in project.dependencies:
            try:
                # this may be a problem when we have circular dependencies? or when we try to debug it...
                child_node, child_unresolved, child_exceptions = self.recursively_resolve_package(dep)
                node.append(child_node)
                unresolved |= child_unresolved
                captured_exceptions.extend(child_exceptions)
            except Exception as ex:
                unresolved.add(dep)
                captured_exceptions.append(ex)
                print(f'  Could not resolve dependency {dep.__module__}.{dep.__qualname__}: {ex}')

        # Remove from unresolved if we were able to process it
        unresolved -= set(self.processed.keys())

        return (node, unresolved, captured_exceptions)

    def materialize_dag(self) -> Node:
        node, unresolved, captured_exceptions = self.recursively_resolve_package(self.root)
        if unresolved:
            print("Some packages could not be resolved:")
            for ex in captured_exceptions:
                print(f"  - {ex}")
            unresolved_tags = ', '.join([x.tag for x in unresolved])
            raise RuntimeError(f"The following packages could not be resolved: {unresolved_tags}")
        return node
