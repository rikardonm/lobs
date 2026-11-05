"""This module resolves the package dependencies and converts package providers into `ResolvedPackage` instances."""

from pathlib import Path

from lobs.machinery.logger import module_logger
from lobs.core.package.base import Package
from lobs.core.dag import Node


class ResolveError(RuntimeError):
    def __init__(self, errors: dict[str, Exception]):
        """An exception where the DAG resolver was unable to complete.

        :param errors: A dict of the package name and its resolve error detail.
        """
        super().__init__()
        self.errors = errors

    def __str__(self) -> str:
        return f"Multiple exceptions when resolving package: {', '.join(self.errors)}"


class _ResolveState:
    def __init__(self):
        self.unresolved: set[type[Package]] = set()
        self.captured_exceptions: dict[str, Exception] = {}
        self.processed: dict[type[Package], Node] = {}


class PackageResolver:
    def __init__(self, root: type[Package], target: Path) -> None:
        self.root = root
        self.target = target
        self.logger = module_logger.getChild(self.__class__.__name__)

    def _build_step(self, current: type[Package]) -> Node:
        pkg_tgt = self.target / current.tag
        pkg_tgt.mkdir(parents=True, exist_ok=True)

        inst = current()

        # First check if all the configuration is fine and dandy
        inst._evaluate_requirements()  # pyright: ignore[reportPrivateUsage]
        # Then we generate the needed files
        inst._prepare_files(pkg_tgt)  # pyright: ignore[reportPrivateUsage]
        inst._validate_configuration()  # pyright: ignore[reportPrivateUsage]
        project = inst._make_project(pkg_tgt)  # pyright: ignore[reportPrivateUsage]

        return Node(inst, project, pkg_tgt)

    def _recursively_resolve_package(
        self,
        current: type[Package],
        state: _ResolveState,
    ) -> Node:
        self.logger.info(f"Resolving package: {current.__module__}.{current.__qualname__}...")
        if x := state.processed.get(current, None):
            return x

        node = self._build_step(current)
        state.processed[current] = node

        for dep in node.project.dependencies:
            try:
                # this may be a problem when we have circular dependencies? or when we try to debug it...
                child_node = self._recursively_resolve_package(dep, state)
                node.append(child_node)
            except Exception as ex:
                state.unresolved.add(dep)
                state.captured_exceptions[dep.__name__] = ex
                self.logger.error(f"Could not resolve dependency {dep.__module__}.{dep.__qualname__}: {ex}")

        # Remove from unresolved if we were able to process it
        state.unresolved -= set(state.processed.keys())

        return node

    def materialize_dag(self) -> Node:
        state = _ResolveState()
        # Invoke the recursive resolution
        top_node = self._recursively_resolve_package(self.root, state)

        if state.unresolved:
            raise ResolveError(state.captured_exceptions)

        return top_node
