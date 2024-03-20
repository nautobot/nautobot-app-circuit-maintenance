<!-- markdownlint-disable MD024 -->

## v1.0.2 - 2024-03-21

### Fixed

- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/pull/293) - Drop bs4 direct dependency and acknowledge dependency on Pydantic 1.x

## v1.0.1 - 2023-09-21

### Added

- [#259](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/259) - Added screenshots to docs/images
- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Added drift management support.

### Changed

- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Changed development tools configuration based on NTC cookiecutter template.
- [#258](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/258) - Migrated to Python 3.8 as minimum.

### Fixed

- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Fixed pylint-nautobot `nb-string-field-blank-null` issues.
- [#267](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/267) - Fixed (by removing) dependency `google-oauth`.

# v1.0 Release

<!-- towncrier release notes start -->

## [v1.0.2 (2024-03-20)](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/releases/tag/v1.0.2)

### Added

- [#249](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/249) - Added in Towncrier.
- [#259](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/259) - Added screenshots to docs/images.
- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Added drift management support.

### Changed

- [#249](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/249) - Migrated to Python 3.7.2 as minimum.
- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Changed development tools configuration based on NTC cookiecutter template.
- [#268](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/268) - Migrated to Python 3.8 as minimum.

### Fixed

- [#261](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/261) - Fixed pylint-nautobot `nb-string-field-blank-null` issues.
- [#267](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/267) - Fixed (by removing) dependency `google-oauth`.

- Update Plugin description in `__init__.py`
- Use new `generic/object_detail.html` base template #232
- Documentation Updates #227 #244 #246
- Enable Upstream Testing #228
- Added Towncrier
- Release 1.0
