# v0.4 Release Notes

This document describes all new features and changes in the release `0.4`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.4.3] - 2021-12-13

### Fixed

- [#172](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/172) Fix potential `DataError: value too long` for type when handling especially long email subjects

## [v0.4.2] - 2021-12-08

### Fixed

- [#163](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/163) Fix inability to refresh OAuth authentication before token expires.
- [#166](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/166) Handle NO-CHANGE status from parser (networktocode/circuit-maintenance-parser#125), handle unknown statuses from parser, fix potential error during nautobot-server post_migrate signal handling.
- [#168](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/168) Discard cached OAuth token if refreshing it fails.

## [v0.4.1] - 2021-11-29

### Fixed

- [#158](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/158) Removed utf-8 decoding for IMAP source to support for ascii encoded emails.

## [v0.4.0] - 2021-11-11

### Added

- [#120](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/120) Added option to apply appropriate labels to Gmail messages after processing them.

### Changed

- [#156](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/issues/156) Circuit CID lookups are now case-insensitive.
