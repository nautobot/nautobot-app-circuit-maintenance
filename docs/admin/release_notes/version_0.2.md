# v0.2 Release Notes

This document describes all new features and changes in the release `0.2`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.2.5] - 2021-10-01

### Added

- [#109](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/109) For Gmail API sources, add a new configuration item limit_emails_with_not_header_from to be used when the source_header is not From to limit the number of notifications received from a mailing list or alias.

### Fixed

- [#113](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/113) In `CircuitMaintenace` detail view, when the parsed notifications are listed, instead of using the date of the parsing action, we show the date when the original notification was sent.
- [#118](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/118) Always create timezone-aware `parser_maintenance` timestamps.
- [#123](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/123) Out-of-sequence notifications could make the final CircuitMaintenance state not reflect the latest notification state. Now, while out-of-sequence notifications will still be processed and linked to the CircuitMaintenance for context, they will not result in a change of its overall state.

## [v0.2.4] - 2021-09-20

### Fixed

- [#108](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/108) Do not use the IntegrityError exception to avoid duplicating entries by verifying that the object exists before creating it.

## [v0.2.3] - 2021-09-17

### Fixed

- [#104](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/104) When creating `RawNotification` we validate the Integrity exception from the DB to avoid postponing the error and handling it gracefully. Also, the `RawNotification.date` is now taken directly from the email notification Date instead of waiting for the parsing output, that will contain the same value in the stamp attribute.

## [v0.2.2] - 2021-09-17

### Fixed

- [#99](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/99) Change uniqueness for `RawNotification`.
- [#100](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/100) Improve traceback formatting in case of exception during `process_raw_notification()`.

## [v0.2.1] - 2021-09-16

### Added

- [#95](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/95) Add `emailmessage` info when getting error due not able to get email sender address.

## [v0.2.0] - 2021-09-15

### Added

- [#81](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/81) Extend Circuit Maintenance ID to include the Provider and the Maintenace ID to make it unique among multiple Providers.
- [#86](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/86) Adopt new circuit-maintenance-parser to simplify email related code. Use stamp from notification to define the date of the RawNotification. Limit the size of the store RawNotification via configuration file.

### Fixed

- [#76](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/76) Fix IMAP authentication logic that was not cleaning session after authentication failure.
- [#85](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/85) Fix how the attach_all_providers feature was updated between restarts.
