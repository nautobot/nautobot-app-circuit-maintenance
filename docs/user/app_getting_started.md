# Getting Started with the App

This document provides a step-by-step tutorial on how to get the App going and how to use it.

## Install the App

To install the App, please follow the instructions detailed in the [Installation Guide](../admin/install.md).

After (or before) installing the Nautobot App, you may want to install the [`Circuit Maintenance Parser` library](https://github.com/networktocode/circuit-maintenance-parser/).

## First steps with the App

After installation of the App, it's time to create some Circuit Maintenances and Notifications!

### Define source emails per Provider

In the Nautobot UI, under **Circuits -> Providers**, for each Provider that we would like to track via the Circuit Maintenance plugin, we **must** configure at least one email source address (or a comma-separated list of addresses) in the **`Custom Fields -> Emails for Circuit Maintenance plugin** field.

### Configure Notification Sources in `nautobot_config.py`

In `nautobot_config.py`, in the `PLUGINS_CONFIG`, under the `nautobot_circuit_maintenance` key, we should define the Notification Sources that will be able later in the UI, where you will be able to **validate** if the authentication credentials provided are working fine or not.

There are two mandatory attributes (other keys are dependent on the integration type, and will be documented below):

- `name`: Name to identify the Source and will be available in the UI.
- `url`: URL to reach the Notification Source (i.e. `imap://imap.gmail.com:993`)

#### Run `nautobot-server post_upgrade` command

The [`nautobot-server post_upgrade`](https://docs.nautobot.com/projects/core/en/stable/administration/nautobot-server/#post_upgrade) command wraps multiple Django built-in management commands. Any time you install or upgrade a plugin, it should be run; additionally, for this plugin to operate properly, whenever you change the notification source configuration in `nautobot_config.py` it should be run again.

#### Add `Providers` to the Notification Sources

In the Circuit Maintenance plugin UI section, there is a **Notification Sources** button (yellow) where you can configure the Notification Sources to track new circuit maintenance notifications from specific providers.

Because the Notification Sources are defined by the configuration, you can only view and edit `providers`, but not `add` or `delete` new Notification Sources via UI or API.

!!! note
Note that for emails from a given Provider to be processed, you must _both_ define a source email address(es) for that Provider (Usage section 1, above) _and_ add that provider to a specific Notification Source as described in this section.

#### Run Handle Notifications Job

There is an asynchronous task defined as a **Nautobot Job**, **Handle Circuit Maintenance Notifications** that will connect to the email sources defined under the Notification Sources section (step above), and will fetch new notifications received since the last notification was fetched.

Each notification will be parsed using the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) library, and if a valid parsing is executed, a new **Circuit Maintenance** will be created, or if it was already created, it will updated with the new data.

So, for each email notification received, several objects will be created:

#### Notification

Each notification received will create a related object, containing the raw data received, and linking to the corresponding **parsed notification** in case the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) was able to parse it correctly.

#### Parsed Notification

When a notification was successfully parsed, it will create a **parsed notification** object, that will contain the structured output from the parser library , following the recommendation defined in [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md), and a link to the related **Circuit Maintenance** object created.

#### Circuit Maintenance

The **Circuit Maintenance** is where all the necessary information related to a Circuit maintenance is tracked, and reuses most of the data model defined in the parser library.

Attributes:

- Name: name or identifier of the maintenance.
- Description: description of the maintenance.
- Status: current state of the maintenance.
- Start time: defined start time of the maintenance work.
- End time: defined end time of the maintenance work.
- Ack: boolean to show if the maintenance has been properly handled by the operator.
- Circuits: list of circuits and its specific impact linked to this maintenance.
- Notes: list of internal notes linked to this maintenance.
- Notifications: list of all the parsed notifications that have been processed for this maintenance.

![Circuit Maintenance Job](../images/circuit_maintenance.png)

## What are the next steps?

- Continue adding new providers referenced in the `NotificationSources` that will bring new maintenances into Nautobot circuits.
- If you find some notification that can't be parsed successfully, open an issue in the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser).
