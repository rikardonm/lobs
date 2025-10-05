"""

See: https://stackoverflow.com/questions/67631/how-can-i-import-a-module-dynamically-given-the-full-path
"""
from pathlib import Path
from types import ModuleType
import importlib.util


def import_module(module_name: str, file: Path) -> ModuleType:
    """Dynamically import a module from a given file path."""
    file = file.absolute()
    if not file.exists():
        raise FileNotFoundError(f"File {file} does not exist.")
    spec = importlib.util.spec_from_file_location(module_name, file)
    assert spec is not None, f"Could not load spec for module {module_name} at {file}"
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None, f"Spec loader is None for module {module_name} at {file}"
    spec.loader.exec_module(module)
    return module
