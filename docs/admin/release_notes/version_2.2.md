# v2.2 Release Notes

<!-- towncrier release notes start -->

## [v2.2.4 (2024-08-08)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.2.4)

### Fixed

- [#312](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/312) - Fixed incorrect reference to nonexistent `raw_notification__date` field that caused errors under Django 4.2.

## [v2.2.3 (2024-07-03)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.2.3)

### Documentation

- [#345](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/345) - Updated app config and urls to populate documentation link.

## [v2.2.2 (2024-06-04)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.2.2)

### Fixed

- [#305](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/305) - Fixed an error at startup if `exchangelib` is not installed.

## [v2.2.1 (2024-06-04)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.2.1)

### Dependencies

- [#303](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/303) - Added backwards-compatibility with Pydantic 1.x.

## [v2.2.0 (2024-06-04)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.2.0)

### Added

- [#284](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/284) - Added feature to support Microsoft Exchange Web Services as an Email platform.

### Changed

- [#298](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/298) - Use proper CustomFieldModelFilterFormMixin instead of CustomFieldCustomFieldFilterForm
- [#302](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/302) - Added FilterForm for CircuitImpact or Note

### Housekeeping

- [#8](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/8) - Re-baked from the latest template.
