"""Types for Circuit Maintenance GraphQL."""
import graphene
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field
from taggit.managers import TaggableManager

from nautobot.extras.graphql.types import TagType

from nautobot_circuit_maintenance import models, filters


@convert_django_field.register(TaggableManager)
def convert_field_to_list_tags(field, registry=None):
    """Convert TaggableManager to List of Tags."""
    return graphene.List(TagType)


class CircuitMaintenanceType(DjangoObjectType):
    """Graphql Type Object for CircuitMaintenace model."""

    class Meta:
        """Meta object boilerplate for CircuitMaintenanceType."""

        model = models.CircuitMaintenance
        filterset_class = filters.CircuitMaintenanceFilterSet


class CircuitImpactType(DjangoObjectType):
    """Graphql Type Object for CircuitImpact model."""

    class Meta:
        """Meta object boilerplate for CircuitImpactType."""

        model = models.CircuitImpact
        filterset_class = filters.CircuitImpactFilterSet


graphql_types = [CircuitMaintenanceType, CircuitImpactType]
