# ruff: noqa: B018
# vulture whitelist — mark false positives below as bare expressions

# console_scripts entry point (pyproject.toml [project.scripts])
validate_main  # codeql[py/ineffectual-statement]

# dataclass fields — vulture can't distinguish from unused variables
kind  # codeql[py/ineffectual-statement]
file  # codeql[py/ineffectual-statement]
other_module_id  # codeql[py/ineffectual-statement]
module_id  # codeql[py/ineffectual-statement]
dependency_id  # codeql[py/ineffectual-statement]
path  # codeql[py/ineffectual-statement]
