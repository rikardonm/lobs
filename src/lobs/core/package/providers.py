"""This module contains classes representing packages and projects that are sourced from the internet."""
from urllib.request import urlretrieve
from urllib.parse import urlparse
from pathlib import Path
import zipfile
import tarfile


class DownloadablePackage:
    def __init__(
        self,
        url: str,
    ) -> None:
        self.url = url

    def _make_archive_filename(self, resolve_path: Path) -> Path:
        parsed = urlparse(self.url)
        return resolve_path / Path(parsed.path).name

    def resolve_to(self, target: Path) -> None:
        """Here we download the package into "a" directory, and populate the files as needed."""
        out_file = self._make_archive_filename(target)
        if not out_file.exists():
            urlretrieve(self.url, out_file)
        # After downloading, we extract the archive "in-place"
        sfs = out_file.suffixes
        if sfs[-1:] == [".zip"]:
            with zipfile.ZipFile(out_file, 'r') as zip_ref:
                zip_ref.extractall(target)
        elif sfs[-2:] in [[".tar", ".gz"], [".tar", ".xz"]]:
            with tarfile.open(out_file, 'r:*') as tar_ref:
                tar_ref.extractall(target, filter=tarfile.fully_trusted_filter)
        else:
            raise ValueError(f"Unsupported archive suffix: {out_file.suffixes}")
