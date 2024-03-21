# v0.3 Release Notes

This document describes all new features and changes in the release `0.3`. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.2] - 2021-10-26

### Fixed

- [#147](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/147) Fix duplicated `CircuitImpact` when circuit ID was present for a Maintenance ID.

## [v0.3.1] - 2021-10-22

### Fixed

- [#142](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/142) Handle Gmail API pagination, enforce subject truncation to 200 characters, and fix notification retrieval comparison.
- [#143](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/143) Fix duplicated `Notes` raising db uniqueness exception.

## [v0.3.0] - 2021-10-19

### Changed

- [#127](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/127) Increase default `raw_notification_size` from 1000 to 8192, and also update this and `raw_notification_initial_days_since` definition in `PLUGINS_CONFIG`. Notice the updates in the app configuration section:

```py
PLUGINS_CONFIG = {
    "nautobot_circuit_maintenance": {
        "raw_notification_initial_days_since": 100,
        "raw_notification_size": 16384,
        "notification_sources": [
            {
              ...
            }
        ]
    }
}
```

- [#128](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/128) Remove date from `RawNotification`, `ParsedNotification` and Note, and adding stamp to `RawNotification` as the reference to when the notification was sent.
- [#129](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/129) Improve efficiency to retrieve default app-metrics preselecting all related tables.
- [#131](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/131) Add ChangeLog tab to `Note` detail view and href from `CircuitMaintenance`.
- [#135](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/135) Simplified GraphQL configuration and add testing.
- [#137](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/137) Update Jobs section name to `CircuitMaintenance`.

### Fixed

- [#134](https://github.com/nautobot/nautobot-app-circuit-maintenance/issues/134) Fix `CircuitImpact` detail view, adding href to `CircuitMaintenance` and Circuit.
