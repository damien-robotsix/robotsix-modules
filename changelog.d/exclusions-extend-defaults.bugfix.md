`excluded_paths` now **extends** the built-in repo-health defaults instead of
replacing them, so a repo names only its own extra scaffolding. Replacing forced
any repo needing one additional exemption to restate the entire default list.
The defaults also gain CODEOWNERS, the JS/TS toolchain configs (`tsconfig.json`,
`vite.config.*`, `vitest.config.*` and friends) and `docs/modules.yaml` itself —
a taxonomy describes a repo's modules and is not one of them.
