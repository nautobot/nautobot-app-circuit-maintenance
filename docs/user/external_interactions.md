# External Interactions

This document describes external dependencies and prerequisites for this App to operate, including system requirements, API endpoints, interconnection or integrations to other applications or services, and similar topics.

## External System Integrations

### From the App to Other Systems

This app utilizes the GMAIL Api to retrieve circuit maintenance notices via email.

## Nautobot API endpoints

### Rest API

The app includes 6 API endpoints to manage its related objects, complete info in the Swagger section.

- Circuit Maintenance: `/api/plugins​/circuit-maintenance​/maintenance`
- Circuit Impact: `/api/plugins​/circuit-maintenance​/circuitimpact`
- Note: `/api/plugins​/circuit-maintenance​/note`

### GraphQL API

Circuit Maintenance and Circuit Impact objects are available for GraphQL queries.
