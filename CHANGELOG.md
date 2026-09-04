# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0](https://github.com/damien-robotsix/robotsix-modules/compare/v0.4.2...v0.5.0) (2026-09-03)


### Features

* Remove unused `.github/actions/python-setup` composite action (dead near-duplicate of `setup`) (20260821T125015Z-remove-unused-github-actions-python-setu-50de) ([#302](https://github.com/damien-robotsix/robotsix-modules/issues/302)) ([8c13605](https://github.com/damien-robotsix/robotsix-modules/commit/8c13605ac88f0d9153cbd0767630553f7b40fc97))


### Bug Fixes

* Make check_coverage surface GitOperationError instead of silently returning [] (non-git checkout) (20260903T202041Z-make-check-coverage-surface-gitoperation-f192) ([#319](https://github.com/damien-robotsix/robotsix-modules/issues/319)) ([66d8c27](https://github.com/damien-robotsix/robotsix-modules/commit/66d8c2795e45f69b256e30c85619dbcc3a413f9c))
* **mill-config:** restore parseable repo settings clobbered by ticket c645 ([#314](https://github.com/damien-robotsix/robotsix-modules/issues/314)) ([db46f91](https://github.com/damien-robotsix/robotsix-modules/commit/db46f913b20d4bde672c2afb57bc35f88ede5005))
* Reconcile excluded_paths EXTEND contract with REPLACE implementation in _find_unclassified (20260903T203002Z-reconcile-excluded-paths-extend-contract-019d) ([#320](https://github.com/damien-robotsix/robotsix-modules/issues/320)) ([7fd5414](https://github.com/damien-robotsix/robotsix-modules/commit/7fd5414b121df5791790cc37e7e223cc5f3c0eb8))

## [0.4.2](https://github.com/damien-robotsix/robotsix-modules/compare/v0.4.1...v0.4.2) (2026-08-09)


### Bug Fixes

* **ci:** add the required description to the Setup composite action ([#274](https://github.com/damien-robotsix/robotsix-modules/issues/274)) ([bc1f944](https://github.com/damien-robotsix/robotsix-modules/commit/bc1f944927a0b468235da89053110ab28e17f17d))

## [0.4.1](https://github.com/damien-robotsix/robotsix-modules/compare/v0.4.0...v0.4.1) (2026-08-09)


### Bug Fixes

* **release:** don't fail lock-sync when the release branch is gone ([#282](https://github.com/damien-robotsix/robotsix-modules/issues/282)) ([8ef1e83](https://github.com/damien-robotsix/robotsix-modules/commit/8ef1e8343ed82ff5f1d08439ee71fd1f3ee619d8))

## [0.4.0](https://github.com/damien-robotsix/robotsix-modules/compare/v0.3.0...v0.4.0) (2026-08-08)


### Features

* **ci:** wire the shared auto-release workflow ([#277](https://github.com/damien-robotsix/robotsix-modules/issues/277)) ([22ccc44](https://github.com/damien-robotsix/robotsix-modules/commit/22ccc44e6b0ec0729b8ef5cc8c49e00fd6b2cd20))
* exempt repo-health paths from the registration check ([#271](https://github.com/damien-robotsix/robotsix-modules/issues/271)) ([9204a1f](https://github.com/damien-robotsix/robotsix-modules/commit/9204a1f04df12a1eea2df559ffeed103f0fbaf91))
* **release:** adopt release-please, retire towncrier ([#280](https://github.com/damien-robotsix/robotsix-modules/issues/280)) ([7ac1818](https://github.com/damien-robotsix/robotsix-modules/commit/7ac18184ec695091ab77425078a342b163764ac2))


### Bug Fixes

* excluded_paths extends the defaults instead of replacing them ([#272](https://github.com/damien-robotsix/robotsix-modules/issues/272)) ([588627e](https://github.com/damien-robotsix/robotsix-modules/commit/588627e59d358ce9d06e42dbb7bbab9eb29cd37f))
* exempt renovate config from the registration check ([#273](https://github.com/damien-robotsix/robotsix-modules/issues/273)) ([26b645f](https://github.com/damien-robotsix/robotsix-modules/commit/26b645ffccbfa795fa15dbfb63930f9936c1994c))


### Reverts

* **ci:** drop auto-release.yml — superseded by release-please ([#278](https://github.com/damien-robotsix/robotsix-modules/issues/278)) ([bf102e0](https://github.com/damien-robotsix/robotsix-modules/commit/bf102e022b86f00d48316383c621ceff368aacd7))

## [0.3.0]

### Features

- `check-registration` no longer demands that repo-health scaffolding be claimed by
  a module. CI workflows, linter and packaging configs, build descriptors, licence
  texts and per-PR changelog fragments are exempt by default, and the new optional
  `excluded_paths` key lets a repo replace that set — an empty list restores full
  coverage. A taxonomy inventories logical modules; on one robotsix repo 61% of
  tracked files were scaffolding it was obliged to account for, and because
  towncrier writes one fragment per pull request, every changelog entry had become a
  taxonomy edit. ([#exclude-repo-health-paths](https://github.com/damien-robotsix/robotsix-modules/issues/exclude-repo-health-paths))

### Bug Fixes

- `renovate.json` and its `.renovaterc` variants join the repo-health defaults.
  Dependency-update automation configures the repository, not a logical module —
  it was the single remaining unclassified file across the whole fleet. ([#exclude-renovate](https://github.com/damien-robotsix/robotsix-modules/issues/exclude-renovate))
- `excluded_paths` now **extends** the built-in repo-health defaults instead of
  replacing them, so a repo names only its own extra scaffolding. Replacing forced
  any repo needing one additional exemption to restate the entire default list.
  The defaults also gain CODEOWNERS, the JS/TS toolchain configs (`tsconfig.json`,
  `vite.config.*`, `vitest.config.*` and friends) and `docs/modules.yaml` itself —
  a taxonomy describes a repo's modules and is not one of them. ([#exclusions-extend-defaults](https://github.com/damien-robotsix/robotsix-modules/issues/exclusions-extend-defaults))
- Removed the towncrier `auto-release.yml` added earlier today. It implements a **superseded** convention: `changelog-driven-releases.md` is marked superseded by `release-please.md`, the fleet-wide release automation. Left in place it would have fired on Monday and pushed a version bump and `v*` tag that release-please is meant to own. ([#20260808T120500Z-revert-auto-release](https://github.com/damien-robotsix/robotsix-modules/issues/20260808T120500Z-revert-auto-release))
- Fix ``python -m robotsix_modules`` to forward the exit code from ``main()`` via ``sys.exit()``, instead of silently returning 0 on validation errors or parse failures. ([#20260801T143604Z-fix-python-m-robotsix-modules-always-ex-0f3a](https://github.com/damien-robotsix/robotsix-modules/issues/20260801T143604Z-fix-python-m-robotsix-modules-always-ex-0f3a))
- fix: `YamlReadError` raised by public `load_taxonomy()` but missing from top-level `__all__` and API docs ([#20260721T170214Z-fix-yamlreaderror-raised-by-public-load-b396](https://github.com/damien-robotsix/robotsix-modules/issues/20260721T170214Z-fix-yamlreaderror-raised-by-public-load-b396))

### Changes

- Remove `exclude-newer = "7 days"` from `[tool.uv]` in `pyproject.toml` to fix Dependabot resolution failures when package updates are published within the 7-day window (e.g., `ruff` 0.16.1). The lock file already guarantees reproducibility. ([#20260803T013815Z-remove-exclude-newer-from-tool-uv-to-fix-8bb5](https://github.com/damien-robotsix/robotsix-modules/issues/20260803T013815Z-remove-exclude-newer-from-tool-uv-to-fix-8bb5))

### Removals

- Remove unused YamlParseError class from _yaml.py ([#20260720T075504Z-remove-unused-yamlparseerror-class-from-3ba1](https://github.com/damien-robotsix/robotsix-modules/issues/20260720T075504Z-remove-unused-yamlparseerror-class-from-3ba1))

### Documentation

- Sync `docs/schema-reference.md` "Complete example" with current `docs/modules.yaml` and add CI check to prevent future drift ([#20260727T093301Z-sync-docs-schema-reference-md-complete-e-3d13](https://github.com/damien-robotsix/robotsix-modules/issues/20260727T093301Z-sync-docs-schema-reference-md-complete-e-3d13))

### Miscellaneous

- [#20260720T003648Z-add-changelog-fragment-reminder-to-pr-te-fa07](https://github.com/damien-robotsix/robotsix-modules/issues/20260720T003648Z-add-changelog-fragment-reminder-to-pr-te-fa07), [#20260722T011312Z-classify-changelog-d-gitkeep-assign-to-r-20e4](https://github.com/damien-robotsix/robotsix-modules/issues/20260722T011312Z-classify-changelog-d-gitkeep-assign-to-r-20e4), [#20260721T012757Z-add-fragment-type-guidance-to-contributi-6e0a](https://github.com/damien-robotsix/robotsix-modules/issues/20260721T012757Z-add-fragment-type-guidance-to-contributi-6e0a), [#20260803T013815Z-ci-failure-uv-in-update-1501089446-on-ma-8bb5](https://github.com/damien-robotsix/robotsix-modules/issues/20260803T013815Z-ci-failure-uv-in-update-1501089446-on-ma-8bb5), [#20260721T014605Z-fix-broken-for-loop-indentation-in-ci-fr-93d7](https://github.com/damien-robotsix/robotsix-modules/issues/20260721T014605Z-fix-broken-for-loop-indentation-in-ci-fr-93d7), [#20260722T020730Z-expose-changelog-md-as-a-changelog-page-35f9](https://github.com/damien-robotsix/robotsix-modules/issues/20260722T020730Z-expose-changelog-md-as-a-changelog-page-35f9), [#20260725T022916Z-robotsix-modules-remove-dead-internal-pe-d61c](https://github.com/damien-robotsix/robotsix-modules/issues/20260725T022916Z-robotsix-modules-remove-dead-internal-pe-d61c), [#20260723T025226Z-add-pytest-test-to-validate-docs-schema-a551](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T025226Z-add-pytest-test-to-validate-docs-schema-a551), [#20260724T034650Z-replace-language-system-hooks-with-langu-58e2](https://github.com/damien-robotsix/robotsix-modules/issues/20260724T034650Z-replace-language-system-hooks-with-langu-58e2), [#20260724T044051Z-add-defense-in-depth-exception-barrier-t-1429](https://github.com/damien-robotsix/robotsix-modules/issues/20260724T044051Z-add-defense-in-depth-exception-barrier-t-1429), [#20260725T052200Z-split-uv-dependency-group-separate-test-929c](https://github.com/damien-robotsix/robotsix-modules/issues/20260725T052200Z-split-uv-dependency-group-separate-test-929c), [#20260725T052200Z-split-uv-dependency-groups](https://github.com/damien-robotsix/robotsix-modules/issues/20260725T052200Z-split-uv-dependency-groups), [#20260720T075933Z-rename-changelog-fragment-from-misc-md-t-5216](https://github.com/damien-robotsix/robotsix-modules/issues/20260720T075933Z-rename-changelog-fragment-from-misc-md-t-5216), [#20260706T081436Z-add-towncrier-check-pre-commit-hook-to-p-2862](https://github.com/damien-robotsix/robotsix-modules/issues/20260706T081436Z-add-towncrier-check-pre-commit-hook-to-p-2862), [#20260706T081436Z-add-towncrier-to-dev-dependencies-and-co-319e](https://github.com/damien-robotsix/robotsix-modules/issues/20260706T081436Z-add-towncrier-to-dev-dependencies-and-co-319e), [#20260706T081436Z-create-scripts-release-convenience-scrip-fa22](https://github.com/damien-robotsix/robotsix-modules/issues/20260706T081436Z-create-scripts-release-convenience-scrip-fa22), [#20260706T081436Z-update-contributing-md-release-checklist-699b](https://github.com/damien-robotsix/robotsix-modules/issues/20260706T081436Z-update-contributing-md-release-checklist-699b), [#20260718T081727Z-robotsix-modules-enable-audit-periodic-w-dd16](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T081727Z-robotsix-modules-enable-audit-periodic-w-dd16), [#20260718T081727Z-robotsix-modules-enable-copy-paste-perio-2157](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T081727Z-robotsix-modules-enable-copy-paste-perio-2157), [#20260718T081727Z-robotsix-modules-enable-repo-description-a5f0](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T081727Z-robotsix-modules-enable-repo-description-a5f0), [#20260718T081728Z-robotsix-modules-enable-state-sync-perio-a9f2](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T081728Z-robotsix-modules-enable-state-sync-perio-a9f2), [#20260718T084059Z-move-pre-commit-hooks-yaml-from-docs-mod-9ecf](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T084059Z-move-pre-commit-hooks-yaml-from-docs-mod-9ecf), [#20260718T084100Z-align-pre-commit-mypy-version-with-pypro-d6a7](https://github.com/damien-robotsix/robotsix-modules/issues/20260718T084100Z-align-pre-commit-mypy-version-with-pypro-d6a7), [#20260719T085054Z-add-uv-malware-check-1-to-ci-uv-sync-ste-41e2](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T085054Z-add-uv-malware-check-1-to-ci-uv-sync-ste-41e2), [#20260720T085333Z-update-docs-schema-reference-md-complete-06b1](https://github.com/damien-robotsix/robotsix-modules/issues/20260720T085333Z-update-docs-schema-reference-md-complete-06b1), [#20260722T090359Z-add-strict-markers-to-pytest-config-in-p-5cd1](https://github.com/damien-robotsix/robotsix-modules/issues/20260722T090359Z-add-strict-markers-to-pytest-config-in-p-5cd1), [#20260722T090359Z-pin-vulture-dev-dependency-with-a-minimu-3dbe](https://github.com/damien-robotsix/robotsix-modules/issues/20260722T090359Z-pin-vulture-dev-dependency-with-a-minimu-3dbe), [#20260723T090953Z-add-exclude-newer-7-days-to-tool-uv-in-p-e715](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T090953Z-add-exclude-newer-7-days-to-tool-uv-in-p-e715), [#20260723T090953Z-add-step-security-harden-runner-to-all-c-ae1c](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T090953Z-add-step-security-harden-runner-to-all-c-ae1c), [#20260723T090953Z-add-uv-lock-check-step-to-ci-to-guard-ag-e076](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T090953Z-add-uv-lock-check-step-to-ci-to-guard-ag-e076), [#20260723T090953Z-deduplicate-scripts-check-and-scripts-li-ce4e](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T090953Z-deduplicate-scripts-check-and-scripts-li-ce4e), [#20260723T090953Z-rename-validate-paths-to-validate-schema-4a50](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T090953Z-rename-validate-paths-to-validate-schema-4a50), [#20260725T092203Z-add-lowest-version-dependency-testing-to-b3bc](https://github.com/damien-robotsix/robotsix-modules/issues/20260725T092203Z-add-lowest-version-dependency-testing-to-b3bc), [#20260725T092203Z-deduplicate-repeated-argument-definition-8d55](https://github.com/damien-robotsix/robotsix-modules/issues/20260725T092203Z-deduplicate-repeated-argument-definition-8d55), [#20260726T092701Z-add-uv-audit-sarif-output-and-upload-to-e4b4](https://github.com/damien-robotsix/robotsix-modules/issues/20260726T092701Z-add-uv-audit-sarif-output-and-upload-to-e4b4), [#20260726T092701Z-split-tests-cli-test-cli-py-into-focused-27a5](https://github.com/damien-robotsix/robotsix-modules/issues/20260726T092701Z-split-tests-cli-test-cli-py-into-focused-27a5), [#20260728T095148Z-add-step-security-harden-runner-to-lockf-bd99](https://github.com/damien-robotsix/robotsix-modules/issues/20260728T095148Z-add-step-security-harden-runner-to-lockf-bd99), [#20260723T095819Z-refactor-validate-main-to-eliminate-dupl-b87c](https://github.com/damien-robotsix/robotsix-modules/issues/20260723T095819Z-refactor-validate-main-to-eliminate-dupl-b87c), [#20260729T102657Z-remove-stale-pydantic-additional-depende-7c75](https://github.com/damien-robotsix/robotsix-modules/issues/20260729T102657Z-remove-stale-pydantic-additional-depende-7c75), [#20260729T102657Z-update-agent-md-pre-commit-hook-list-to-8f4f](https://github.com/damien-robotsix/robotsix-modules/issues/20260729T102657Z-update-agent-md-pre-commit-hook-list-to-8f4f), [#20260731T111304Z-resolve-circular-dependency-between-find-2f56](https://github.com/damien-robotsix/robotsix-modules/issues/20260731T111304Z-resolve-circular-dependency-between-find-2f56), [#20260801T111820Z-create-tests-validation-test-paths-py-an-7d63](https://github.com/damien-robotsix/robotsix-modules/issues/20260801T111820Z-create-tests-validation-test-paths-py-an-7d63), [#20260805T115222Z-add-version-pins-to-unpinned-dependencie-646b](https://github.com/damien-robotsix/robotsix-modules/issues/20260805T115222Z-add-version-pins-to-unpinned-dependencie-646b), [#20260805T143001Z-add-version-pins-to-all-5-unpinned-pre-c-27a1](https://github.com/damien-robotsix/robotsix-modules/issues/20260805T143001Z-add-version-pins-to-all-5-unpinned-pre-c-27a1), [#20260802T152349Z-robotsix-modules-enable-mypy-baseline-pe-df63](https://github.com/damien-robotsix/robotsix-modules/issues/20260802T152349Z-robotsix-modules-enable-mypy-baseline-pe-df63), [#20260802T152458Z-align-local-pytest-coverage-gate-fail-un-b956](https://github.com/damien-robotsix/robotsix-modules/issues/20260802T152458Z-align-local-pytest-coverage-gate-fail-un-b956), [#20260801T153054Z-remove-stale-duplicate-changelog-fragmen-650c](https://github.com/damien-robotsix/robotsix-modules/issues/20260801T153054Z-remove-stale-duplicate-changelog-fragmen-650c), [#20260719T154210Z-robotsix-modules-enable-changelog-autofi-6f3e](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T154210Z-robotsix-modules-enable-changelog-autofi-6f3e), [#20260803T160731Z-subprocess-test-the-installed-robotsix-m-61fa](https://github.com/damien-robotsix/robotsix-modules/issues/20260803T160731Z-subprocess-test-the-installed-robotsix-m-61fa), [#20260804T161930Z-robotsix-modules-enable-pin-bump-periodi-8429](https://github.com/damien-robotsix/robotsix-modules/issues/20260804T161930Z-robotsix-modules-enable-pin-bump-periodi-8429), [#20260805T162502Z-switch-lowest-deps-test-ci-job-to-uv-res-6f48](https://github.com/damien-robotsix/robotsix-modules/issues/20260805T162502Z-switch-lowest-deps-test-ci-job-to-uv-res-6f48), [#20260805T163115Z-extend-shared-conftest-error-path-helper-f539](https://github.com/damien-robotsix/robotsix-modules/issues/20260805T163115Z-extend-shared-conftest-error-path-helper-f539), [#20260716T163127Z-robotsix-modules-enable-completeness-che-ca19](https://github.com/damien-robotsix/robotsix-modules/issues/20260716T163127Z-robotsix-modules-enable-completeness-che-ca19), [#20260806T164607Z-self-test-the-published-validate-module-dc2d](https://github.com/damien-robotsix/robotsix-modules/issues/20260806T164607Z-self-test-the-published-validate-module-dc2d), [#20260717T165142Z-docs-check-coverage-missing-from-docs-in-3365](https://github.com/damien-robotsix/robotsix-modules/issues/20260717T165142Z-docs-check-coverage-missing-from-docs-in-3365), [#20260717T165142Z-fix-compute-default-globs-missing-from-t-ae44](https://github.com/damien-robotsix/robotsix-modules/issues/20260717T165142Z-fix-compute-default-globs-missing-from-t-ae44), [#20260714T165300Z-robotsix-modules-enable-baseline-periodi-4602](https://github.com/damien-robotsix/robotsix-modules/issues/20260714T165300Z-robotsix-modules-enable-baseline-periodi-4602), [#20260716T165528Z-docs-findingkind-missing-from-mkdocs-api-9c37](https://github.com/damien-robotsix/robotsix-modules/issues/20260716T165528Z-docs-findingkind-missing-from-mkdocs-api-9c37), [#20260716T165528Z-fix-configstructureerror-is-defined-expo-910c](https://github.com/damien-robotsix/robotsix-modules/issues/20260716T165528Z-fix-configstructureerror-is-defined-expo-910c), [#20260722T165851Z-fix-yamlconfigerror-defined-but-never-re-de17](https://github.com/damien-robotsix/robotsix-modules/issues/20260722T165851Z-fix-yamlconfigerror-defined-but-never-re-de17), [#20260719T170034Z-fix-configparseerror-defined-exported-ca-bf2a](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T170034Z-fix-configparseerror-defined-exported-ca-bf2a), [#20260720T170219Z-fix-add-main-py-to-enable-python-m-robot-5e2b](https://github.com/damien-robotsix/robotsix-modules/issues/20260720T170219Z-fix-add-main-py-to-enable-python-m-robot-5e2b), [#20260721T172634Z-rename-changelog-fragment-from-misc-md-t-e209](https://github.com/damien-robotsix/robotsix-modules/issues/20260721T172634Z-rename-changelog-fragment-from-misc-md-t-e209), [#20260714T174225Z-remove-unused-rewrite-in-glob-paths-vers-3619](https://github.com/damien-robotsix/robotsix-modules/issues/20260714T174225Z-remove-unused-rewrite-in-glob-paths-vers-3619), [#20260802T183654Z-agent-md-ci-invariants-never-let-tool-co-1865](https://github.com/damien-robotsix/robotsix-modules/issues/20260802T183654Z-agent-md-ci-invariants-never-let-tool-co-1865), [#20260715T192538Z-robotsix-modules-enable-module-curator-p-c827](https://github.com/damien-robotsix/robotsix-modules/issues/20260715T192538Z-robotsix-modules-enable-module-curator-p-c827), [#20260724T201352Z-robotsix-modules-enable-module-size-peri-52a0](https://github.com/damien-robotsix/robotsix-modules/issues/20260724T201352Z-robotsix-modules-enable-module-size-peri-52a0), [#20260715T202234Z-classify-changelog-d-assign-changelog-fr-2b25](https://github.com/damien-robotsix/robotsix-modules/issues/20260715T202234Z-classify-changelog-d-assign-changelog-fr-2b25), [#20260719T232926Z-robotsix-modules-enable-docstring-covera-daa6](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T232926Z-robotsix-modules-enable-docstring-covera-daa6), [#20260719T232926Z-robotsix-modules-enable-health-periodic-e5eb](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T232926Z-robotsix-modules-enable-health-periodic-e5eb), [#20260719T232926Z-robotsix-modules-enable-survey-periodic-80b2](https://github.com/damien-robotsix/robotsix-modules/issues/20260719T232926Z-robotsix-modules-enable-survey-periodic-80b2)


## 0.0.0 (unreleased)

### Added

- Added version pins to previously unpinned dependencies in `pyproject.toml` and `.pre-commit-config.yaml` to prevent supply-chain breakage from unvetted releases
- Remove `exclude-newer = "7 days"` from `[tool.uv]` in `pyproject.toml` to fix Dependabot resolution failures when package updates are published within the 7-day window (e.g., `ruff` 0.16.1). The lock file already guarantees reproducibility.
- Add `mypy_baseline` periodic workflow to track mypy error counts over time and detect type regressions.
- Align local coverage threshold with CI: raise `[tool.coverage.report] fail_under` from 80 to 90 in `pyproject.toml` and update documentation references in `CONTRIBUTING.md` accordingly.
- Extract `_glob_paths`, `_has_glob_metacharacters`, and `compute_default_globs`
  from `registration.py` into a new private `_paths.py` module to resolve a
  circular dependency with `_findings.py`.
- Update AGENT.md pre-commit hook list to accurately reflect the current
  `.pre-commit-config.yaml`: replace `detect-secrets` with `gitleaks`, and
  add missing hooks (`zizmor`, `towncrier check`, `validate-pyproject`,
  `mdformat`, `markdownlint-cli2`, `pre-commit-hooks` suite).
- Add CI job `lowest-deps-test` that runs the test suite against the lowest compatible dependency versions (`uv sync --resolution lowest`), catching minimum-version gaps in declared ranges.

### Removed

- Deduplicate repeated CLI argument definitions (`--verbose`, `--output-format`, `--root`) across subcommands by extracting them into a shared `_add_common_args` helper in `src/robotsix_modules/cli/__init__.py`.
- Remove dead internal periodic config files (`state_sync.yaml` and `security_posture.yaml`) that were silently rejected by the mill loader.
- Enable `module_size` periodic workflow to monitor source/test file sizes and propose split tickets for oversized modules.
- Add exception barrier to `main()` and `validate_main()` so unexpected
  runtime errors produce a user-friendly message and `ExitCode.FATAL` (2)
  instead of a raw Python traceback.
- Replace `language: system` pre-commit hooks (vulture, towncrier-check) with
  `language: python` + `additional_dependencies` for deterministic, isolated
  environments. Added `pre-commit>=4.4.0` to dev dependencies.
- Add `[tool.uv] exclude-newer = "7 days"` to prevent CI from
  resolving packages published in the last 7 days, closing the
  window between a malicious upload and its advisory publication.
- Deduplicate `scripts/check` and `scripts/lint` by having `scripts/check` call `scripts/lint` for the shared toolchain (ruff check, ruff format, mypy, markdownlint, mdformat), keeping only the CI-unique steps (deptry, bandit, uv audit, pytest, check-registration, mkdocs build) directly.
- Extract `_emit_results` helper in `validate_main` to eliminate duplicated output-format dispatch logic, reducing nesting depth from 5 to 3.
- Removed unused `YamlConfigError` class from `_yaml.py` (the sole subclass `YamlReadError` now inherits directly from `ConfigError`).
- Rename `_validate_paths` → `_validate_schema_batch` in `src/robotsix_modules/cli/__init__.py` to clarify that the function runs schema validation (not path validation) across multiple files.
- Pin `vulture` dev dependency to `>=2.16` in `pyproject.toml` to match the version locked in `uv.lock` and prevent silent breakage on regeneration.
- Add `--strict-markers` to pytest `addopts` in `pyproject.toml` to catch unregistered marker typos.
- Expose CHANGELOG.md as a Changelog page on the MkDocs site via the existing hook pattern (on_pre_build copy, on_post_build remove) and a new nav entry.
- Classify `changelog.d/.gitkeep` under the `root` module in `docs/modules.yaml` so the registration check passes.
- Exported `YamlReadError` via `robotsix_modules.__all__` so callers of `load_taxonomy()` can catch it without importing from the private `_yaml` module.
- Added fragment-type guidance to CONTRIBUTING.md and PR template, and CI validation
  to catch unknown fragment types before merge, preventing invisible changelog entries
  when `towncrier build` is run for the first release.
- Add ``__main__.py`` shim so ``python -m robotsix_modules`` works (delegates to ``cli:main()``).
- Updated the "Complete example" in `docs/schema-reference.md` to match the
  current `docs/modules.yaml`: added the `root` module, moved
  `.pre-commit-hooks.yaml` from `docs` to `root`, and added `_exceptions.py`
  to the `validation` module paths.
- Removed the unused `YamlParseError` exception class from `_yaml.py`, which was never raised or imported anywhere in the codebase.
- Enable `survey` periodic agent with `.robotsix-mill/periodic/survey.yaml`.
- Add periodic docstring_coverage agent config to `.robotsix-mill/periodic/docstring_coverage.yaml`.
- Add `.robotsix-mill/periodic/health.yaml` to enable the health periodic agent, which inspects the codebase across eight dimensions (test coverage, linting, dependency freshness, CI completeness, documentation, etc.) and proposes draft tickets for newly-discovered gaps.
- `read_yaml_file` now raises `ConfigParseError` (instead of the internal `YamlParseError`) when a file contains invalid YAML, matching the public API contract documented in the package docstring.
- Enable the `changelog_autofill` periodic task to auto-commit changelog entries for PRs with a failing changelog CI check.
- Fixed duplicate `run:` key in `.github/actions/setup/action.yml` that caused `UV_MALWARE_CHECK` env var to be ignored during `uv sync`
- Bump `mirrors-mypy` pre-commit hook from v2.1.0 to v2.3.0 to align with the
  `mypy>=2.2.0` dev dependency, ensuring consistent type-checking across all
  environments.
- Move `.pre-commit-hooks.yaml` from the `docs` module to the `root` module in `docs/modules.yaml` (the file is a repo-root pre-commit hook manifest, not documentation).
- Add `repo_description_sync` periodic workflow to keep the forge description aligned with the README.
- Enable `state_sync` periodic workflow to cross-reference `FindingKind` enum members against string-literal reference sites across the codebase.
- Enable `audit` periodic agent (`.robotsix-mill/periodic/audit.yaml`)
- Add `copy_paste` periodic workflow (`.robotsix-mill/periodic/copy_paste.yaml`) to detect copy-paste duplication across the repository via jscpd.
- Re-export `compute_default_globs` from the top-level `robotsix_modules` package and document it in the API reference and quick-start index.
- Add `check_coverage` to the Public API list in `docs/index.md`
- `ConfigStructureError` is now raised by `read_yaml_file` when the parsed YAML root is not a mapping (previously `YamlParseError` was raised for both invalid-YAML and non-mapping cases). Fixed a stale `InvalidConfigStructureError` docstring reference in `load_taxonomy`.
- Add `FindingKind` to `docs/validation/api.md` members list to ensure it renders in the generated API docs and avoids broken cross-references.
- Enable `completeness_check` periodic agent to scan internal wiring of the robotsix-modules tool itself.
- Added `changelog.d/**` to the `root` module's paths in `docs/modules.yaml`.
- Enable `module_curator` periodic agent to curate the reference `docs/modules.yaml` taxonomy
- Remove Python 3.12 version-portable `**` glob rewrite workaround from `_glob_paths`.
  The project now requires Python >=3.14 where `Path.glob("**")` natively matches files.
- Enable baseline periodic agents (`test_gap`, `bc_check`, `security_posture`) via `.robotsix-mill/periodic/` presence files.
- Create `changelog.d/` directory for towncrier-managed changelog fragments.
- Add `towncrier-check` pre-commit hook (repo: local) to validate changelog fragments.
- Updated the release checklist in `CONTRIBUTING.md` to use the towncrier-based
  workflow: `towncrier build --yes` to generate the changelog, commit the
  updated `CHANGELOG.md` and deleted fragments, and `gh release create` with
  draft notes from `towncrier build --draft`.
- Deduplicate `CODE_OF_CONDUCT.md`: keep single canonical copy at repo root,
  remove `docs/` symlink, and use a MkDocs build-time hook to supply the
  file during documentation builds.
- Remove all periodic mill workflows from `.robotsix-mill/periodic/` to pause auto-generated ticket flooding (audit, survey, completeness_check, test_gap, security_posture, and others). Workflows can be restored individually by re-adding their `.yaml` files.
- Enforce `check-registration` in CI (new `check-registration` job in `ci.yml`) and in the local `scripts/check` script, closing a gap where unregistered files could silently drift out of sync with `docs/modules.yaml`.
- Introduce `FindingKind(StrEnum)` in `src/robotsix_modules/validation/_findings.py` to replace magic-string finding kinds (`"unclassified_file"`, `"stale_path"`, `"duplicate_registration"`, `"path_not_found"`, `"glob_empty"`). All source, test, and README usage sites now reference the enum members instead of raw string literals.
- Register root-level `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `.robotsix-mill/**`, and `scripts/**` under the `root` module's path list in `docs/modules.yaml`, closing remaining `unclassified_file` findings from `check-registration`.
- Remove unused `RobotsixModulesError` import from `robotsix_modules.cli`.)
- Register `src/robotsix_modules/_exceptions.py` in the `validation` module's path list in `docs/modules.yaml`.
- Confirm `docs/CODE_OF_CONDUCT.md` is already a symlink (`-> ../CODE_OF_CONDUCT.md`, created in PR #133); no code change needed to eliminate the byte-identical clone.)
- Revert cosmetic `...` added by prior attempt to root `CONTRIBUTING.md`. The
  core deduplication (`docs/CONTRIBUTING.md` as symlink to `../CONTRIBUTING.md`)
  was already in place from a prior PR; no further changes needed.
- Updated `docs/schema-reference.md` to document the `package` field, correct the `paths` requirement from mandatory to optional (convention globs are synthesised from `package`), and refresh the complete example to match the current `docs/modules.yaml`.
- Add `.github/workflows/lint-workflows.yml` to run actionlint and zizmor on push/PR, using the shared reusable workflow from `robotsix-github-workflows`.
- Add custom exception hierarchy: `RobotsixModulesError` base class with typed subclasses `GitOperationError`, `ConfigError`, `ConfigFileNotFoundError`, `ConfigParseError`, and `ConfigStructureError`. Git-operation failures now raise `GitOperationError` instead of bare `RuntimeError`.
- Remove the retired `robotsix-yaml-config` dependency. The package now uses
  PyYAML directly for all YAML I/O via its internal `_yaml` wrapper, matching
  the config-standard migration to `robotsix-config`.

### Fixed
- Fixed stale docstring in `robotsix_modules.validation.schemas` package init referencing non-existent `robotsix_modules.schemas` path.
- Stale GitHub org URLs in `CONTRIBUTING.md` and `.github/ISSUE_TEMPLATE/config.yml` replaced `robotsix/robotsix-modules` → `damien-robotsix/robotsix-modules`.

### Added
- Added `towncrier>=25.8.0` to dev dependencies and configured `[tool.towncrier]` for changelog management.
- Add `paths` globs to the `cli` module in `docs/modules.yaml` to properly claim its source, test, and doc files.
- Classify validation subpackage files under the `validation` module in `docs/modules.yaml` (11 files now claimed via glob paths).
- Resolve mypy strict-mode errors in test files: add type annotations to conftest helpers, add `types-PyYAML` dev dependency, and fix TestMigrate type signatures.
- Add coverage check to `validate` and `validate-main` subcommands: every tracked file must be covered by at least one module's globs (explicit paths + convention defaults). Previously only `check-registration` performed this check; now the pre-commit `robotsix-modules-validate` hook also catches unclassified files.
- Add ``robotsix-modules migrate`` CLI subcommand that rewrites a
  ``modules.yaml`` to strip explicit path entries already covered by
  convention default globs (``src/<pkg>/<id>/**``, ``tests/<id>/**``,
  ``docs/<id>/**``). Supports ``--in-place`` for file overwrite.
  YAML comments are not preserved.
- Make module ``paths`` optional in ``modules.yaml``: when a top-level
  ``package`` field is set, modules without explicit paths inherit three
  convention globs (``src/<package>/<id>/**``, ``tests/<id>/**``,
  ``docs/<id>/**``).  Add ``compute_default_globs`` to the public API.
- Dogfood `.pre-commit-hooks.yaml` in own `.pre-commit-config.yaml` via `repo: .` instead of `repo: local`.
  Document the pre-commit hook layout convention in `AGENT.md` (## Project layout).
- Added `.pre-commit-hooks.yaml` at repo root enabling remote-repo consumption of the `validate-module-taxonomy` hook (`language: python`)
- Updated `docs/cli/usage.md` — split the pre-commit integration section into two separate code blocks: a remote-repo (recommended) example and the existing local-hook block
- Add `.github/workflows/dependabot-auto-merge.yml` to auto-merge Dependabot PRs once required checks pass.
- Add robotsix-standards reference link to `README.md` and `AGENT.md`.
- Migrate secret scanning from `detect-secrets` to `gitleaks` in both pre-commit and CI, and add a minimal `.gitleaks.toml` configuration.
- Extract `RegistrationFinding` dataclass and its six helper functions from `registration.py` into a new `validation/_findings.py` module for improved cohesion.
- Consolidate duplicate CLI error-path test boilerplate: added shared helpers in `tests/conftest.py` (`run_missing_file_test`, `run_invalid_yaml_test`, `run_root_flag_respected_test`) and replaced 7 per-class duplicate methods in `tests/cli/test_cli.py` with 3 parametrized module-level tests.
- Bump bandit[toml] requirement from >=1.8 to >=1.9.4
- Bump pre-commit hook versions: `pre-commit-hooks` v5.0.0→v6.0.0,
  `ruff` v0.15.15→v0.15.19, `mirrors-mypy` v1.19.1→v2.1.0,
  `zizmor` v1.23.1→v1.26.1
- Add `detect-secrets` CI job to `.github/workflows/ci.yml` for server-side secret scanning with existing baseline
- Update pinned GitHub Actions to latest versions: `actions/checkout` to v7.0.0, `astral-sh/setup-uv` to v8.2.0, `github/codeql-action/upload-sarif` to v4.36.2, `actions/upload-artifact` to v7.0.1. Correct misleading version comment on `codeql-action/upload-sarif`. (mill: Update stale GitHub Actions to latest pinned versions across CI workflows (20260701T092348Z-update-stale-github-actions-to-latest-pi-a566))
- Add `security_posture` periodic workflow to `.robotsix-mill/periodic/` for automated security posture review.
- Document CLI JSON output field schemas for `validate`, `check-registration`, and `validate-paths` subcommands in `docs/cli/usage.md`.
- `CODE_OF_CONDUCT.md`: adopt Contributor Covenant v2.1 with enforcement guidelines and
  reporting contact (`damien.robotsix@gmail.com`).
- `CONTRIBUTING.md`: replace informal "License & conduct" section with a formal code of
  conduct reference and reporting instructions.
- `README.md`: add `## Contributing` section with Contributor Covenant badge and links
  to contributing guide and code of conduct.
- Added `ExitCode` IntEnum (`src/robotsix_modules/cli/_exit_codes.py`) to replace
  raw integer exit codes in the CLI, with named members `OK`, `ERRORS`, and `FATAL`.
- Register `docs/CODE_OF_CONDUCT.md` in the `docs` module's path list in `docs/modules.yaml`.
- `mkdocs.yml`: enable `strict: true` and `validation` block (omitted files, absolute
  links, unrecognized links, anchors) so `mkdocs build --strict` catches broken nav
  entries, orphaned files, and stale cross-references at build time.
- `.github/workflows/ci.yml`: add `mkdocs-build` job that runs `mkdocs build --strict`
  on every PR.
- `scripts/check`: add `mkdocs build --strict` step after pytest so local development
  mirrors the CI docs gate.

### Changed

- `src/robotsix_modules/validation/registration.py`: add explicit `check=False` to
  `subprocess.run()` call and remove unused `# noqa: S607` directive.

### Added

- OpenSSF Scorecard workflow (`.github/workflows/scorecard.yml`) running weekly
  and on push to `main`, with SARIF results uploaded to CodeQL for supply-chain
  security visibility.
- OpenSSF Scorecard badge in `README.md`.
- `.github/workflows/ci.yml`: add `dependency-review` job using
  `actions/dependency-review-action@v5` with `fail-on-severity: moderate` to catch
  vulnerable dependency changes on pull requests.
- `validate-pyproject` pre-commit hook and CI job to validate `pyproject.toml`
  against PEP 517/518/621/639/735 JSON Schemas, catching invalid classifier
  values, malformed dependency specs, and incorrect project metadata fields.
- `zizmor` static analysis for GitHub Actions workflow security: added to
  pre-commit hooks, CI pipeline (with SARIF upload), and dev dependencies.
- `validate-pyproject-schema-store[all]` as an additional dependency for the
  `validate-pyproject` hook and CI job, extending validation to third-party
  `[tool.*]` sections (ruff, mypy, pytest, coverage, deptry, bandit).
- Added `load_schema` to the public API surface of `robotsix_modules.validation`
  and `robotsix_modules` (`__all__` and top-level re-export).
- Replaced `pip-audit` with native `uv audit` for vulnerability scanning and
  `uv export --format cyclonedx1.5` for SBOM generation in CI.
- Markdown linting and formatting via `.markdownlint-cli2.jsonc`, pre-commit
  hooks (`markdownlint-cli2`, `mdformat`), and `scripts/lint`/`scripts/check`
  integration.
- `.gitignore` entries for `site/`, `wheel-env/`, `sbom.json`, `.env`, and
  `.DS_Store` to prevent accidental commits of docs build output, CI artifacts,
  and OS/environment files.

### Fixed

- Suppress ruff S607 (`start-process-with-partial-path`) on intentional `git ls-files`
  subprocess call in `registration.py`.
- Added `types: [markdown]` filter to the `markdownlint-cli2` pre-commit hook,
  preventing it from linting non-Markdown files (Python, YAML, JSON, etc.).
- Added missing `docs/cli/**` path glob to the `cli` module in
  `docs/modules.yaml`, classifying the previously unclaimed `docs/cli/usage.md`
  and completing the per-module layout for the CLI module.
- Added `docs` dependency group (`mkdocs-material`, `mkdocstrings[python]`) to
  `pyproject.toml` and updated `scripts/docs` to use `--group docs`, fixing a
  broken local docs preview (`uv run mkdocs serve` failed without the
  dependencies).
- Added `ignore_errors = true` for the `vulture_whitelist` module in mypy
  configuration, fixing a type-check failure caused by intentional bare names
  in the vulture whitelist file.
- CI: fix local-action-resolution failure by adding explicit `actions/checkout`
  step before each `uses: ./.github/actions/setup` call and removing checkout
  from within the composite action.
- Add empty `tracing` extra to `[project.optional-dependencies]` to satisfy
  reusable workflow's `uv sync --extra tracing` call.

### Changed

- Refactored `validate_main` to use a shared `_validate_paths` generator,
  reducing nesting depth and eliminating the duplicated `for path in args.paths`
  loop.
- Updated dev dependencies: ruff 0.15.16 → 0.15.18, pip-audit 2.10.0 → 2.10.1.

## [0.2.0]

### Added

- `check_registration()` – verifies every tracked file is claimed by exactly one
  module, detecting unclassified files, stale paths, and duplicate
  registrations.
- `validate_paths()` – checks that every module path entry (literal or glob)
  resolves to at least one file on disk.
- `RegistrationFinding` and `PathFinding` frozen-dataclass types for structured
  findings.
- CLI subcommands: `robotsix-modules check-registration` and
  `robotsix-modules validate-paths`, each with `--root` flag and exit-code
  semantics (0/1/2).
- Public API re-exports for the new functions and types from the package root.

## [0.1.0]

Initial public release.

### Added

- JSON-Schema-driven (draft 2020-12) validation for the `docs/modules.yaml`
  module-taxonomy file, with the canonical schema bundled in the package.
- CLI (`robotsix-modules validate`, plus the `robotsix-modules-validate`
  pre-commit wrapper entry point) and Python API (`validate`, `validate_file`,
  `load_taxonomy`, `SCHEMA_PATH`).
- Test suite with coverage enforced at the 80% threshold in CI.
- Quality and security tooling in CI: Ruff (lint + format), mypy, deptry,
  bandit, and pip-audit.
