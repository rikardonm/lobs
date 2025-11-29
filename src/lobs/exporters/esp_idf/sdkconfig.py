"""Types and generator for sdkconfig files."""
import typing as t

from pathlib import Path


FVT: t.TypeAlias = Path | str | bool | int | float | None | t.Callable[[], str]
FT: t.TypeAlias = dict[str, FVT]


def generate_file(config_flags: FT, output_path: Path) -> None:
    """Generate an sdkconfig file from the given configuration flags.

    Args:
        config_flags: A dictionary of configuration flags.
        output_path: The path to the output sdkconfig file.
    """
    gen_assets_path = output_path.with_name("generated_assets")
    gen_assets_path.mkdir(exist_ok=True, parents=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for key, value in config_flags.items():
            if value is True:
                line = f"{key}=y"
            elif value is False or value is None:
                line = f"# {key} is not set"
            elif isinstance(value, (str, Path)):
                line = f'{key}="{value}"'
            elif callable(value):
                line = f'{key}={value()}'
            else:
                line = f'{key}={value}'
            f.write(line + "\n")
