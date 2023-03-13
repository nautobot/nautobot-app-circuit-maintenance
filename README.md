# Circuit Maintenance

<p align="center">
  <img src="https://raw.githubusercontent.com/nautobot/nautobot-plugin-circuit-maintenance/develop/docs/images/icon-nautobot-circuit-maintenance.png" class="logo" height="200px">
  <br>
  <a href="https://github.com/nautobot/nautobot-plugin-circuit-maintenance/actions"><img src="https://github.com/nautobot/nautobot-plugin-circuit-maintenance/actions/workflows/ci.yml/badge.svg?branch=main"></a>
  <a href="https://docs.nautobot.com/projects/circuit-maintenance/en/latest"><img src="https://readthedocs.org/projects/nautobot-plugin-circuit-maintenance/badge/"></a>
  <a href="https://pypi.org/project/nautobot-circuit-maintenance/"><img src="https://img.shields.io/pypi/v/nautobot-circuit-maintenance"></a>
  <a href="https://pypi.org/project/nautobot-circuit-maintenance/"><img src="https://img.shields.io/pypi/dm/nautobot-circuit-maintenance"></a>
  <br>
  An <a href="https://www.networktocode.com/nautobot/apps/">App</a> for <a href="https://nautobot.com/">Nautobot</a>.
</p>

## Overview

A plugin for [Nautobot](https://github.com/nautobot/nautobot) to easily handle Circuit Maintenances related to Nautobot Circuits.

`nautobot-circuit-maintenance` lets you handle maintenances for your Circuits based on notifications received via email by leveraging [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser), a notifications parser library for multiple network service providers that exposes structured data following a recommendation defined in this [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md).

### Screenshots

More screenshots can be found in the [Using the App](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/user/app_use_cases/) page in the documentation. Here's a quick overview of some of the plugin's added functionality:

![Circuit Maintenance Dashboard](https://raw.githubusercontent.com/nautobot/nautobot-plugin-circuit-maintenance/develop/docs/images/dashboard.png)

![Example Circuit Maintenance View](https://raw.githubusercontent.com/nautobot/nautobot-plugin-circuit-maintenance/develop/docs/images/circuit_maintenance.png)

![Example Raw Notifications View](https://raw.githubusercontent.com/nautobot/nautobot-plugin-circuit-maintenance/develop/docs/images/circuit_notifications.png)


## Try it out!

This App is installed in the Nautobot Community Sandbox found over at [demo.nautobot.com](https://demo.nautobot.com/)!

> For a full list of all the available always-on sandbox environments, head over to the main page on [networktocode.com](https://www.networktocode.com/nautobot/sandbox-environments/).

## Documentation

Full documentation for this App can be found over on the [Nautobot Docs](https://docs.nautobot.com) website:

- [User Guide](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/user/app_overview/) - Overview, Using the App, Getting Started.
- [Administrator Guide](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/admin/install/) - How to Install, Configure, Upgrade, or Uninstall the App.
- [Developer Guide](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/dev/contributing/) - Extending the App, Code Reference, Contribution Guide.
- [Release Notes / Changelog](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/admin/release_notes/).
- [Frequently Asked Questions](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/user/faq/).

### Contributing to the Documentation

You can find all the Markdown source for the App documentation under the [`docs`](https://github.com/nautobot/nautobot-plugin-circuit-maintenance/tree/develop/docs) folder in this repository. For simple edits, a Markdown capable editor is sufficient: clone the repository and edit away.

If you need to view the fully-generated documentation site, you can build it with [MkDocs](https://www.mkdocs.org/). A container hosting the documentation can be started using the `invoke` commands (details in the [Development Environment Guide](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/dev/dev_environment/#docker-development-environment)) on [http://localhost:8001](http://localhost:8001). Using this container, as your changes to the documentation are saved, they will be automatically rebuilt and any pages currently being viewed will be reloaded in your browser.

Any PRs with fixes or improvements are very welcome!

## Questions

For any questions or comments, please check the [FAQ](https://docs.nautobot.com/projects/circuit-maintenance/en/latest/user/faq/) first. Feel free to also swing by the [Network to Code Slack](https://networktocode.slack.com/) (channel `#nautobot`), sign up [here](http://slack.networktocode.com/) if you don't have an account.
