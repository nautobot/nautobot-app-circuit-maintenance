# App Overview

This document provides an overview of the App including critical information and import considerations when applying it to your Nautobot environment.

!!! note
    Throughout this documentation, the terms "app" and "plugin" will be used interchangeably.

## Description

A plugin for [Nautobot](https://github.com/nautobot/nautobot) to easily handle Circuit Maintenance events related to Circuits in Nautobot.

`nautobot-circuit-maintenance` lets you handle provider maintenances for your Circuits based on notifications received by email through leveraging [circuit-maintenance-parser](https://github.com/networktocode/circuit-maintenance-parser), a maintenance notification parser library for multiple network service providers that exposes structured data following a recommendation defined in this [draft NANOG BCOP](https://github.com/jda/maintnote-std/blob/master/standard.md), in addition to supporting text based parsing to extract maintenance dates, impacted circuits, and severity of the maintenance.

## Audience (User Personas) - Who should use this App?

This app is meant for any set of users that have to be aware of and administer Circuit Maintenance events within their remit. Both administrators and operators are aided by seeing exactly which circuits, which locations, and this which users and services will be affected by provider maintenance. 

## Authors and Maintainers

Author: @chadell

Maintainers:

- @chadell
- @glennmatthews
- @pke11y
- @scetron
