"""MkDocs hooks — generate files at build time that should not be committed."""

import shutil
from pathlib import Path


def on_pre_build(config):
    """Copy root CODE_OF_CONDUCT.md into docs/ so the nav entry resolves."""
    root = Path(config.config_file_path).parent
    src = root / "CODE_OF_CONDUCT.md"
    dst = root / "docs" / "CODE_OF_CONDUCT.md"
    if src.exists() and not dst.exists():
        shutil.copy2(src, dst)


def on_post_build(config):
    """Remove the generated doc so nothing lingers on disk."""
    root = Path(config.config_file_path).parent
    generated = root / "docs" / "CODE_OF_CONDUCT.md"
    if generated.exists():
        generated.unlink()
