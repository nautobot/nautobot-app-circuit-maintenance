# Changelog

## v0.1.6 - 2021-07-14

### Added

- #36 - Add Gmail API OAuth Source type to Notification Sources

## v0.1.5 - 2021-06-25

### Fixed

- #32 - Fix permissions to list `NotificationSources` in navigation menu
- #33 - Add proper migration of Source field for `RawNotification`

## v0.1.4 - 2021-06-23

### Changed

- #23 - Make notifications more agnostic to multiple source types and improve `RawNotification` model
- #25 - Add a Validation view for Notification Sources
- #26 - Add Gmail API Service Account Source type to Notification Sources
- #27 - Improve Notification Source UX
- #28 - Bump `circuit-maintenance-parser` to version 1.2.1

### Fixed

- #24 - Fix Bulk Edit Notification Source

## v0.1.3 - 2021-06-10

### Fixed

- #19 - Fix Readme format

## v0.1.2 - 2021-06-10

### Fixed

- #11 - Fix images links from PyPI

### Changed

- #13 - Move Notification Source secrets to configuration.py and refactor class to get ready for new integrations

## v0.1.1 - 2021-05-14

### Fixed

- #8 - fix NotificationSource update with previous password
- #8 - fix Custom Validator update
- #8 - Rename EmailSettingsServer model to NotificationSource

## v0.1.0 - 2021-05-03

Initial release
