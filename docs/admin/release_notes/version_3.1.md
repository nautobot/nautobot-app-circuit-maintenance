# v3.1 Release Notes

This document describes all new features and changes in the release. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Release Overview

- Removed the django-cryptography dependency and fixed Django 5.2 compatibility.
- Documentation updated with new screenshots, alongside minor UI and maintenance improvements.

<!-- towncrier release notes start -->

## [v3.1.1 (2026-04-10)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v3.1.1)

### Housekeeping

- Rebaked from the cookie `nautobot-app-v3.1.3`.

## [v3.1.0 (2026-03-25)](https://github.com/nautobot/nautobot-app-circuit-maintenance/releases/tag/v3.1.0)

### Fixed

- [#370](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/370) - Fixed upstream testing for django 5.2 by removing django-cryptography dependency and fixing migration that depended on it.

### Documentation

- [#367](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/367) - Updated Circuit maintenance documentation to include 3.0 screenshots.

### Housekeeping

- [#357](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/357) - Added navigation icon/weight and removed the unused 'add' button.
- [#360](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/360) - Bump release version.
- Rebaked from the cookie `nautobot-app-v3.0.0`.
- Rebaked from the cookie `nautobot-app-v3.1.2`.
