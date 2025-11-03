import abc
from pathlib import Path
import typing as t

from lobs._machinery.logger import module_logger
from lobs.core.resolver import Node
from .configuration import ExporterConfiguration


T = t.TypeVar('T', bound=ExporterConfiguration)


class BaseExporter(abc.ABC):
    def __init__(self, root_node: Node, base_output_path: Path) -> None:
        self.logger = module_logger.getChild(f"{self.__class__.__name__}")
        self.base_output_path = base_output_path
        self.root_node = root_node
        self._flat_node_list: list[Node] = []
        self.__collect_dependencies_for_node(self.root_node)

    @abc.abstractmethod
    def _export_node(self, node: Node) -> None:
        """Export the project to the desired format."""

    def __collect_dependencies_for_node(self, node: Node) -> None:
        if node in self._flat_node_list:
            return
        self._flat_node_list.append(node)
        for child in node.children:
            self.__collect_dependencies_for_node(child)

    def export(self) -> None:
        """Export the project to the desired format."""
        # traverse and build the nodes; but we build them bottom-first
        # and so, for that, we traverse the tree from the root and collect all dependencies
        for node in self._flat_node_list[::-1]:
            self._export_node(node)


IExporter: t.TypeAlias = BaseExporter
