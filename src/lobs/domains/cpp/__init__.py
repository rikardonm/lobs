# SPDX-FileCopyrightText: 2025-present Ricardo Marchesan <ricardo@azevem.com>
#
# SPDX-License-Identifier: MIT
# flake8: noqa: F401
# pyright: reportUnusedImport = false
from . import project
from .compiler_options import CompilationFlags

__all__ = [
    "project",
    "CompilationFlags",
]
