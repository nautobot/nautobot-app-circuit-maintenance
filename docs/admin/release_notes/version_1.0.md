<!-- markdownlint-disable MD024 -->

!!! warning "Developer Note - Remove Me!"
    Guiding Principles:

    - Changelogs are for humans, not machines.
    - There should be an entry for every single version.
    - The same types of changes should be grouped.
    - Versions and sections should be linkable.
    - The latest version comes first.
    - The release date of each version is displayed.
    - Mention whether you follow Semantic Versioning.

    Types of changes:

    - `Added` for new features.
    - `Changed` for changes in existing functionality.
    - `Deprecated` for soon-to-be removed features.
    - `Removed` for now removed features.
    - `Fixed` for any bug fixes.
    - `Security` in case of vulnerabilities.


This document describes all new features and changes in the release `1.0`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Major features or milestones
- Achieved in this `x.y` release
- Changes to compatibility with Nautobot and/or other apps, libraries etc.

## [v1.0.1] - 2021-09-08

### Added

- [#259](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/259) - Added screenshots to docs/images
- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Added drift management support.

### Changed

- [#261](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/261) - Changed development tools configuration based on NTC cookiecutter template.
- [#258](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/258) - Migrated to Python 3.8 as minimum.

### Fixed

- [#123](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/123) Fixed Tag filtering not working in job launch form

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
