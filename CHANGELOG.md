# Changelog

## v0.2.2 - 2021-09-17

### Fix

- #99: Change uniqueness for `RawNotification`.

## v0.2.1 - 2021-09-16

### Added

- #95: Add `emailmessage` info when getting error due not able to get email sender address.

## v0.2.0 - 2021-09-15

### Added

- #81: Extend Circuit Maintenance ID to include the Provider and the Maintenace ID to make it unique among multiple Providers.
- #86, #88: Adopt new `circuit-maintenance-parser` to simplify email related code. Use `stamp` from notification to define the date of the `RawNotification`. Limit the size of the store `RawNotification` via configuration file.

### Fixed

- #76: Fix IMAP authentication logic that was not cleaning session after authentication failure.
- #85: Fix how the attach_all_providers feature was updated between restarts.

## v0.1.10 - 2021-09-01

### Added

- #73: Add new application metric: `circuit_maintenance_status` to show the circuit status depending on related Circuit Maintenances.
- #78: Add optional `extra_scopes` config parameter to use with Gmail notification sources.

### Fixed

- #74: Fix Gmail API `after` format.

## v0.1.9 - 2021-08-12

### Changed

- Bump `circuit-maintenance-parser` to v1.2.3 to accept more `click` versions and do not conflict with `nautobot` 1.1.2.

## v0.1.8 - 2021-08-12

### Added

- #51: Add a Custom Field in Provider, `provider_parser_circuit_maintenances` to allow custom mapping of the provider type class used from the `circuit-maintenance-parser` library.
- #54: Add a plugin option to define the number of days back to retrieve notifications on the first run of the plugin, before it has one previous notification as a reference.
- #63: Add a `attach_all_providers` flag in the `NotificationSource` plugin config to signal that any new Provider added will be automatically attached to the `NotificationSource`.

### Changed

- #51: Improve Development Environment and upgrade Nautobot version to 1.1.0

### Fixed

- #53: The **SINCE** filter to receive email notifications is extended on day in the past in order to get notifications from the same day as the last notifications stored.
- #61: Add rendering of `custom_fields` and `relationships` in all the detail_views of the plugin, `tags` in `PrimaryModel` detail view and the `export` action button on the object list views.
- #62: Fix Href from Circuit to related Circuit Maintenances.

## v0.1.7 - 2021-07-27

### Added

- #42:
  - Add stack trace to job log on exception
  - IMAP and GMail notification sources now support a `source_header` configuration parameter to allow for cases where `From` is not the relevant header to inspect.

### Fixed

- #42:
  - Avoid an exception if some Providers do not have a populated `emails_circuit_maintenance` value
  - `extract_email_source()` now correctly handles email addresses containing dash characters.
  - Avoid an exception on processing a non-multipart email payload
  - Don't try to create a `RawNotification` if no `raw_payload` could be extracted from the notification.

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
