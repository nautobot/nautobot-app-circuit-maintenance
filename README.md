# Nautobot Circuit Maintenance plugin

A plugin for [Nautobot](https://github.com/nautobot/nautobot) to easily handle Circuit Maintenances related to Nautobot Circuits.

`nautobot-circuit-maintenance` lets you handle maintenances for your Circuits based on notifications received by email by leveraging on [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser), a notifications parser library for multiple network service providers that exposes structured data following a recommendation defined in this [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md).

## Installation

The plugin is available as a Python package in pypi and can be installed with pip

```shell
pip install nautobot-circuit-maintenance
```

> The plugin is compatible with Nautobot 1.0.0b4 and higher

To ensure Circuit Maintenance is automatically re-installed during future upgrades, create a file named `local_requirements.txt` (if not already existing) in the Nautobot root directory (alongside `requirements.txt`) and list the `nautobot-circuit-maintenance` package:

```no-highlight
# echo nautobot-circuit-maintenance >> local_requirements.txt
```

Once installed, the plugin needs to be enabled in your `configuration.py`

```python
# In your configuration.py
PLUGINS = ["nautobot_circuit_maintenance"]

# PLUGINS_CONFIG = {
#   "nautobot_circuit_maintenance": {
#     ADD YOUR SETTINGS HERE
#   }
# }
```

> Note: there is no current need to define any custom settings for this plugin

## Usage

All the plugin configuration is done via UI, under the **Plugins** tab, in the **Circuit Maintenance** sections.

### 1. Define source emails per provider

Each Circuit **Provider**, that we would like to track via the Circuit Maintenance plugin, requires at least one email address under the `Custom Fields -> Emails for Circuit Maintenance plugin` section.
These are the source email addresses that the plugin will check and use to classify each notification for each specific provider.

### 2. Configure Email settings

In the Circuit Maintenance plugin UI section, there is a **settings** button (yellow) where you can configure multiple email sources to track for new circuit maintenance notifications.

<p align="center">
<img src="./docs/images/email_config.png" width="500">
</p>

Attributes:

- Email: email address
- Password: password to access the email service API for this service
- URL: email service URL
- Server Type: type of email service. Currently, only GMAIL is supported.
- Providers: list of Ciruit Providers that will be tracked.

> [How to setup Gmail with App Passwords](https://support.google.com/accounts/answer/185833)

### 3. Run Handle Notifications Job

There is an asynchronous task defined as a **Nautobot Job**, **Handle Circuit Mainentance Notifications** that will connect to the emails sources defined under the Settings section (step above), and will fetch new notifications received since the last notification was fetched.
Each notification will be parsed using the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) library, and if a valid parsing is executed, a new **Circuit Maintenance** will be created, or if it was already created, it will updated with the new data.

So, for each email notification received, several objects will be created:

#### 3.1 Notification

Each notification received will create a related object, containing the raw data received, and linking to the corresponding **parsed notification** in case the [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser) was able to parse it correctly.

#### 3.2 Parsed Notification

When a notification was successfully parsed, it will create a **parsed notification** object, that will contain the structured output from the parser library , following the recommendation defined in [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md), and a link to the related **Circuit Maintenance** object created.

#### 3.3 Circuit Maintenance

The **Circuit Maintenance** is where all the necessary information related to a Circuit maintenance is tracked, and reuses most of the data model defined in the parser library.

Attributes:

- Name: name or identifier of the maintenance.
- Description: description of the maintenance.
- Status: current state of the maintenance.
- Start time: defined start time of the maintenance work.
- End time: defined end time of the maintenance work.
- Acknowledged: boolean to show if the maintenance has been properly handled by the operator.
- Circuits: list of circuits and its specific impact linked to this maintenance.
- Notes: list of internal notes linked to this maintenance.
- Notifications: list of all the parsed notifications that have been processed for this maintenance.

<p align="center">
<img src="./docs/images/circuit_maintenance.png" width="800" class="center">
</p>

### Rest API

The plugin includes 6 API endpoints to manage its related objects, complete info in the Swagger section.

- Circuit Maintenance: `/api/plugins​/circuit-maintenance​/maintenance`
- Circuit Impact: `/api/plugins​/circuit-maintenance​/maintenance-circuitimpact`
- Circuit Note: `/api/plugins​/circuit-maintenance​/maintenance-note`
- Raw Notification: `/api/plugins​/circuit-maintenance​/raw-notification`
- Parsed Notification: `/api/plugins​/circuit-maintenance​/parsed-notification`
- Settings: `/api/plugins​/circuit-maintenance​/settings`

### GraphQL API

Circuit Maintenance and Circuit Impact objects are available for GraphQL queries.

## Contributing

Pull requests are welcomed and automatically built and tested against multiple version of Python and multiple version of Nautobot through TravisCI.

The project is packaged with a light development environment based on `docker-compose` to help with the local development of the project and to run the tests within TravisCI.

The project is following Network to Code software development guideline and is leveraging:

- Black, Pylint, Bandit and pydocstyle for Python linting and formatting.
- Django unit test to ensure the plugin is working properly.

### CLI Helper Commands

The project is coming with a CLI helper based on [invoke](http://www.pyinvoke.org/) to help setup the development environment. The commands are listed below in 3 categories `dev environment`, `utility` and `testing`.

Each command can be executed with `invoke <command>`. All commands support the arguments `--nautobot-ver` and `--python-ver` if you want to manually define the version of Python and Nautobot to use. Each command also has its own help `invoke <command> --help`

#### Local dev environment

```no-highlight
  build            Build all docker images.
  debug            Start Nautobot and its dependencies in debug mode.
  destroy          Destroy all containers and volumes.
  restart          Restart Nautobot and its dependencies.
  start            Start Nautobot and its dependencies in detached mode.
  stop             Stop Nautobot and its dependencies.
```

#### Utility

```no-highlight
  cli              Launch a bash shell inside the running Nautobot container.
  create-user      Create a new user in django (default: admin), will prompt for password.
  makemigrations   Run Make Migration in Django.
  nbshell          Launch a nbshell session.
```

#### Testing

```no-highlight
  bandit           Run bandit to validate basic static code security analysis.
  black            Run black to check that Python files adhere to its style standards.
  flake8           This will run flake8 for the specified name and Python version.
  pydocstyle       Run pydocstyle to validate docstring formatting adheres to NTC defined standards.
  pylint           Run pylint code analysis.
  tests            Run all tests for this plugin.
  unittest         Run Django unit tests for the plugin.
```

## Questions

For any questions or comments, please check the [FAQ](FAQ.md) first and feel free to swing by the [Network to Code slack channel](https://networktocode.slack.com/) (channel #nautobot).
Sign up [here](http://slack.networktocode.com/)
