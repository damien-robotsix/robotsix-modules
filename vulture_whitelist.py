# vulture whitelist — reference names below to mark them as intentionally used.
# The names are passed to a no-op function so the module is never executed but
# vulture and CodeQL both treat the references as real uses.


def _keep(*_names: object) -> None:
    """No-op: keep referenced names alive for vulture/CodeQL."""


_keep(
    validate_main,  # console_scripts entry point (pyproject.toml [project.scripts])
    kind,  # dataclass field
    file,  # dataclass field
    other_module_id,  # dataclass field
    module_id,  # dataclass field
    dependency_id,  # dataclass field
    path,  # dataclass field
)
