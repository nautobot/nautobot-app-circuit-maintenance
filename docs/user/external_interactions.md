# External Interactions

This document describes external dependencies and prerequisites for this App to operate, including system requirements, API endpoints, interconnection or integrations to other applications or services, and similar topics.

!!! warning "Developer Note - Remove Me!"
    Optional page, remove if not applicable.

## External System Integrations

### From the App to Other Systems

### From Other Systems to the App

## Nautobot API endpoints

### Rest API

The plugin includes 6 API endpoints to manage its related objects, complete info in the Swagger section.

- Circuit Maintenance: `/api/plugins​/circuit-maintenance​/maintenance`
- Circuit Impact: `/api/plugins​/circuit-maintenance​/circuitimpact`
- Note: `/api/plugins​/circuit-maintenance​/note`

### GraphQL API

Circuit Maintenance and Circuit Impact objects are available for GraphQL queries.
