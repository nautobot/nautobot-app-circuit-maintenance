<!-- markdownlint-disable MD024 -->

## v1.0.1 - 2023-09-21

### Added

- [#259](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/259) - Added screenshots to docs/images
- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Added drift management support.

### Changed

- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Changed development tools configuration based on NTC cookiecutter template.
- [#258](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/258) - Migrated to Python 3.8 as minimum.

### Fixed

- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Fixed pylint-nautobot `nb-string-field-blank-null` issues.
- [#267](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/267) - Fixed (by removing) dependency `google-oauth`.

# v1.0 Release

<!-- towncrier release notes start -->
## [v1.0.1 (2023-09-29)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v1.0.1)

### Added

- [#249](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/249) - Added in Towncrier.
- [#259](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/259) - Added screenshots to docs/images.
- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Added drift management support.

### Changed

- [#249](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/249) - Migrated to Python 3.7.2 as minimum.
- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Changed development tools configuration based on NTC cookiecutter template.
- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Added related ORM object to jobs logging messages.
- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Renamed Job `nautobot_circuit_maintenance.jobs.site_search.FindSitesWithMaintenanceOverlap` => `nautobot_circuit_maintenance.jobs.location_search.FindLocationsWithMaintenanceOverlap`.
- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Renamed `PLUGINS_CONFIG.nautobot_circuit_maintenance.metrics.labels_attached.site` => `PLUGINS_CONFIG.nautobot_circuit_maintenance.metrics.labels_attached.location`.
- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Updated `nautobot-capacity-metrics` dependency to `>=3`.
- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Updated `nautobot` dependency to `>=2`.
- [#268](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/268) - Migrated to Python 3.8 as minimum.

### Fixed

- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Fixed pylint-nautobot `nb-string-field-blank-null` issues.
- [#267](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/267) - Fixed (by removing) dependency `google-oauth`.

### Removed

- [#262](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/262) - Removed `NotificationSource.slug` field.


- Update App description in `__init__.py`
- Use new `generic/object_detail.html` base template #232
- Documentation Updates #227 #244 #246
- Enable Upstream Testing #228
- Added Towncrier
- Release 1.0
