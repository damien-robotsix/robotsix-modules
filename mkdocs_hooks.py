"""MkDocs hooks — generate files at build time that should not be committed."""

import shutil
from pathlib import Path


def on_pre_build(config):
    """Copy root files into docs/ so the nav entries resolve."""
    root = Path(config.config_file_path).parent
    for name in ("CODE_OF_CONDUCT.md", "CHANGELOG.md"):
        src = root / name
        dst = root / "docs" / name
        if src.exists() and not dst.exists():
            shutil.copy2(src, dst)


def on_post_build(config):
    """Remove the generated docs so nothing lingers on disk."""
    root = Path(config.config_file_path).parent
    for name in ("CODE_OF_CONDUCT.md", "CHANGELOG.md"):
        generated = root / "docs" / name
        if generated.exists():
            generated.unlink()
