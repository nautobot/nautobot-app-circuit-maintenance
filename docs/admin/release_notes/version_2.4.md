# v2.4 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Fixed a potential sensitive data disclosure issue in the REST API and logging in the "Update Circuit Maintenances" job.
- Changed minimum Nautobot version to 2.4.20.
- Dropped support for Python versions 3.8 and 3.9.

<!-- towncrier release notes start -->
## [v2.4.0 (2025-12-09)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v2.4.0)

### Security

- [#336](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/336) - Removed the password and credentials from the serialization of the Source object.
- [#336](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/336) - Updated logging messages to prevent logging sensitive data from the Source object.

### Dependencies

- [#340](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/340) - Pinned Django debug toolbar to <6.0.0.

### Housekeeping

- [#344](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/344) - Refactored CircuitMaintenance, CircuitImpact, Note, NotificationSource model related UI views to use `NautobotUIViewSet`.
- Rebaked from the cookie `nautobot-app-v2.4.1`.
- Rebaked from the cookie `nautobot-app-v2.4.2`.
- Rebaked from the cookie `nautobot-app-v2.5.0`.
- Rebaked from the cookie `nautobot-app-v2.5.1`.
- Rebaked from the cookie `nautobot-app-v2.6.0`.
- Rebaked from the cookie `nautobot-app-v2.7.0`.
- Rebaked from the cookie `nautobot-app-v2.7.1`.
- Rebaked from the cookie `nautobot-app-v2.7.2`.
