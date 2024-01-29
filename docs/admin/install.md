# Installing the App in Nautobot

Here you will find detailed instructions on how to **install** and **configure** the App within your Nautobot environment.

## Prerequisites

- The app is compatible with Nautobot 2.0.0 and higher.
- Databases supported: PostgreSQL, MySQL

!!! note
Please check the [dedicated page](compatibility_matrix.md) for a full compatibility matrix and the deprecation policy.

### Access Requirements

You will need access to an email account that receives provider maintenance notifications.

## Install Guide

!!! note
    Apps can be installed manually or using Python's `pip`. See the [nautobot documentation](https://nautobot.readthedocs.io/en/latest/plugins/#install-the-package) for more details. The pip package name for this app is [`nautobot-circuit-maintenance`](https://pypi.org/project/nautobot-circuit-maintenance/).

The app is available as a Python package via PyPI and can be installed with `pip`:

```shell
pip install nautobot-circuit-maintenance
```

To ensure Circuit Maintenance is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-circuit-maintenance` package:

```shell
echo nautobot-circuit-maintenance >> local_requirements.txt
```

Once installed, the app needs to be enabled in your Nautobot configuration. The following block of code below shows the additional configuration required to be added to your `nautobot_config.py` file:

- Append `"nautobot_circuit_maintenance"` to the `PLUGINS` list.
- Append the `"nautobot_circuit_maintenance"` dictionary to the `PLUGINS_CONFIG` dictionary and override any defaults.

```python
# In your nautobot_config.py
PLUGINS = ["nautobot_circuit_maintenance"]

PLUGINS_CONFIG = {
    "nautobot_circuit_maintenance": {
        "raw_notification_initial_days_since": 100,
        "raw_notification_size": 16384,
        "dashboard_n_days": 30,  # Defaults to 30 days in the configurations, change/override here
        "overlap_job_exclude_no_impact": False, # Exclude in job warnings the impact of `No-Impact`
        "notification_sources": [
            {
              ...
            }
        ]
    }
}
```

Once the Nautobot configuration is updated, run the Post Upgrade command (`nautobot-server post_upgrade`) to run migrations and clear any cache:

```shell
nautobot-server post_upgrade
```

Then restart (if necessary) the Nautobot services which may include:

- Nautobot
- Nautobot Workers
- Nautobot Scheduler

```shell
sudo systemctl restart nautobot nautobot-worker nautobot-scheduler
```

## App Configuration

The app behavior can be controlled with the following list of settings:

The app behavior can be controlled with the following list of settings:

| Key     | Example | Default | Description                          |
| ------- | ------ | -------- | ------------------------------------- |
| `enable_backup` | `True` | `True` | A boolean to represent whether or not to run backup configurations within the app. |
| `platform_slug_map` | `{"cisco_wlc": "cisco_aireos"}` | `None` | A dictionary in which the key is the platform slug and the value is what netutils uses in any "network_os" parameter. |
| `per_feature_bar_width` | `0.15` | `0.15` | The width of the table bar within the overview report |
