"""This module contains classes representing packages and projects that are sourced from the internet."""
from dataclasses import dataclass
from urllib.request import urlretrieve
from urllib.parse import urlparse
from pathlib import Path
import zipfile
import tarfile

import git
import git.exc


@dataclass
class DownloadablePackage:
    url: str

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


@dataclass
class GitRepoPackage:
    repo_url: str
    ref: str

    def resolve_to(self, target: Path) -> None:
        if not target.exists():
            target.mkdir(parents=True, exist_ok=True)
        try:
            repo = git.Repo(target)
        except git.exc.InvalidGitRepositoryError:
            repo = git.Repo.clone_from(
                self.repo_url,
                target,
                multi_options=["--depth", "1", "--branch", self.ref]
            )
            repo.git.execute([
                "git",
                "config",
                "--global",
                "--add",
                "safe.directory",
                str(target),
            ])
        # Check that the reported version is what we expect
        _tag = repo.git.execute(["git", "describe", "--tags"])
        if _tag != self.ref:
            raise ValueError(
                f"Checked out ref {_tag} does not match expected {self.ref}."
                " Clean up the project to rebuild."
            )
