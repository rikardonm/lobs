"""This module contains classes representing packages and projects that are sourced from the internet."""
from urllib.request import urlretrieve
from urllib.parse import urlparse
from pathlib import Path
import typing as t
import zipfile
import tarfile


class DownloadablePackage:
    def __init__(
        self,
        url: str,
        archive_suffix: t.Literal["zip", "tar.gz", "tar.xz"] | None = None,
    ) -> None:
        self.url = url
        self.archive_suffix = archive_suffix

    def _make_archive_filename(self, resolve_path: Path) -> Path:
        parsed = urlparse(self.url)
        filename = Path(parsed.path).name
        if '.' in filename:
            filename, suffix = filename.split('.', 1)
        else:
            if not self.archive_suffix:
                raise RuntimeError("Could not determine archive suffix from URL; please provide one.")
            suffix = self.archive_suffix
        return resolve_path / (filename + "." + suffix)

    def resolve_to(self, target: Path) -> None:
        """Here we download the package into "a" directory, and populate the files as needed."""
        out_file = self._make_archive_filename(target)
        if not out_file.exists():
            urlretrieve(self.url, out_file)
        # After downloading, we extract the archive "in-place"
        match out_file.suffixes:
            case [".zip"]:
                with zipfile.ZipFile(out_file, 'r') as zip_ref:
                    zip_ref.extractall(target)
            case [".tar", ".gz"] | [".tar", ".xz"]:
                with tarfile.open(out_file, 'r:*') as tar_ref:
                    tar_ref.extractall(target, filter=tarfile.fully_trusted_filter)
            case _:
                raise ValueError(f"Unsupported archive suffix: {out_file.suffixes}")
