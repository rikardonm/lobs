import abc
from pathlib import Path
import typing as t

from lobs.machinery.logger import module_logger
if t.TYPE_CHECKING:
    from lobs.core.resolver import Node
else:
    Node = t.Any


class ExporterConfiguration:
    """The configuration for the exporter.

    This class can be extended by exporters to add custom configuration options.
    """


TCFG = t.TypeVar('TCFG', bound=ExporterConfiguration)


class GenericExporter(abc.ABC, t.Generic[TCFG]):
    def __init_subclass__(cls) -> None:
        # Get the generic configuration type
        try:
            cls.config_type: type[TCFG] = t.get_args(cls.__orig_bases__[0])[0]
        except (AttributeError, IndexError):
            raise RuntimeError("Could not determine the ExporterConfiguration type for the exporter.")
        return super().__init_subclass__()

    @classmethod
    def _get_config_for_node(
        cls,
        node: Node,
        config_type: type[TCFG],
        gen_path: Path,
    ) -> TCFG:
        """Get the exporter configuration for the given node and exporter configuration type."""
        cfg = node.package.get_exporter_configuration(config_type, gen_path)
        return cfg or cls.config_type()

    def __init__(self, root_node: Node, base_output_path: Path) -> None:
        self.logger = module_logger.getChild(f"{self.__class__.__name__}")
        self.base_output_path = base_output_path
        self.root_node = root_node
        self._flat_node_list: list[Node] = []
        gen_path = self.base_output_path / "gen"
        gen_path.mkdir(exist_ok=True, parents=True)
        self._config = self._get_config_for_node(self.root_node, self.config_type, gen_path)
        self.__collect_dependencies_for_node(self.root_node)

    @abc.abstractmethod
    def _export_node(self, node: Node, config: TCFG) -> None:
        """Export the project to the desired format."""

    def __collect_dependencies_for_node(self, node: Node) -> None:
        if node in self._flat_node_list:
            return
        self._flat_node_list.append(node)
        for child in node.children:
            self.__collect_dependencies_for_node(child)

    def export(self) -> None:
        """Export the project to the desired format.

        The nodes are built bottom-first.
        """
        # traverse and build the nodes; but we build them bottom-first
        # and so, for that, we traverse the tree from the root and collect all dependencies
        for node in self._flat_node_list[::-1]:
            node_gen_assets_path = node.resolved_path / "gen"
            node_gen_assets_path.mkdir(exist_ok=True, parents=True)
            config = self._get_config_for_node(node, self.config_type, node_gen_assets_path)
            self._export_node(node, config)


BaseExporter = GenericExporter[ExporterConfiguration]
