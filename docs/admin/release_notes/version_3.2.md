# v3.2 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- The Notification Source detail page now uses the Nautobot UI Component Framework, which restores compatibility with Nautobot 3.2.9 and later.
- Fixed an open redirect in the Notification Source "Validate Authentication" action.
- The minimum supported Nautobot version is now 3.1.0; Nautobot 3.0.x is no longer supported.
- Updated development and documentation dependencies to address open Dependabot security alerts.

<!-- towncrier release notes start -->

## [v3.2.0 (2026-11-23)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v3.2.0)

### Security

- [#414](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/414) - Fixed an open redirect in the Notification Source "Validate Authentication" action, which followed any `return_url` query parameter without validation; off-site URLs are now ignored and the action redirects to the Notification Source detail page.
- Updated dependencies to address open Dependabot security alerts, including Nautobot 3.1.8, Django 5.2.19, oauthlib 4.0.1, PyJWT 2.15.1, urllib3 2.8.0, and mkdocs-material 9.7.7.

### Changed

- [#414](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/414) - The Notification Source detail page now lists only the providers the user has permission to view, and the duplicate Edit button below the info panel was removed in favor of the standard header Edit button.
- Raised the minimum supported Nautobot version to 3.1.0; Nautobot 3.0.x is no longer supported.

### Fixed

- [#414](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/414) - Migrated the Notification Source detail view to the UI Component Framework so its "Validate Authentication" action no longer renders the legacy detail template, fixing compatibility with upcoming Nautobot releases.
- Fixed the `post_upgrade` command name in the upgrade guide and the empty compatibility note in the install guide.

### Housekeeping

- [#418](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/418) - Updating CODEOWNERS
- Rebaked from the cookie `nautobot-app-v3.1.4`.
