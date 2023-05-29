# Architecture Decision Records

## Circuit Maintenance Parser

The Circuit Maintenance Parser library is separated from the Nautobot Plugin to increase its usability outside of situations where Nautobot may not be installed or may be too heavy of tool in a specific use case. This also allows us to decouple plugin development from parser development.
