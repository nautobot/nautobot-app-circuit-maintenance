# v0.6 Release Notes

This document describes all new features and changes in the release `0.6`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.6.2] - 2023-01-30

### Added

- [#221](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/221) Adds `watchmedo` to auto reload worker containers during job development.

### Changed

- [#234](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/234) Unpin `pydantic` from dependencies, and use the one from the `circuit-maintenance-parser`.
- [#230](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/230) Update init.py to better describe the app in the UI.

### Fixed

- [#221](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/221) Fixes where duplicate maintenance records show jobs.

## [v0.6.1] - 2022-10-28

### Added

- [#214](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/214) Maintenance Overlap Job Addition.

### Fixed

- [#222](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/222) Fix for circuit maintenance detail view. Show approriate A and Z termination sides.
- [#216](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/216) Fix variable naming in Overlapping Maintenance Job: start_date instead of start_time.
- [#208](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/208) Fix CI credentials.

## [v0.6.0] - 2022-09-14

### Added

- [#191](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/191) Add Dashboard View.
- [#187](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/187) Add maintenance start date to Circuit Maintenance extension in Device detail view.

### Changed

- [#195](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/195) Drop Python 3.6 support.
- [#182](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/182) Add Readme reference to `post_upgrade`.
- [#180](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/180) Update dependency `google-auth-oauthlib` to ^0.5.0.
