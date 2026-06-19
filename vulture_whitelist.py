# ruff: noqa: B018
# vulture whitelist — mark false positives below as bare expressions

# console_scripts entry point (pyproject.toml [project.scripts])
validate_main

# dataclass fields — vulture can't distinguish from unused variables
kind
file
other_module_id
module_id
path
