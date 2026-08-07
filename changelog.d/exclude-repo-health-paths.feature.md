`check-registration` no longer demands that repo-health scaffolding be claimed by
a module. CI workflows, linter configs, licence texts and per-PR changelog
fragments are exempt by default, and the new optional `excluded_paths` key lets
a repo replace that set — an empty list restores full coverage. A taxonomy
inventories logical modules; on one robotsix repo 61% of tracked files were
scaffolding it was obliged to account for, and because towncrier writes one
fragment per pull request, every changelog entry had become a taxonomy edit.
