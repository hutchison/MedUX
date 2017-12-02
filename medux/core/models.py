"""
MedUX - A Free/OpenSource Electronic Medical Record
Copyright (C) 2017 Christian González

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from .fields import *


class Coding(models.Model):
    """http://build.fhir.org/datatypes-definitions.html#Coding"""

    # The identification of the code system that defines the meaning of the symbol in the code.
    system = UriField(blank=True)

    # The version of the code system which was used when choosing this code.
    version = models.CharField(max_length=35, blank=True)

    # A symbol in syntax defined by the system. The symbol may be a predefined code
    # or an expression in a syntax defined by the coding system (e.g. post-coordination).
    code = CodeField()

    # A representation of the meaning of the code in the system, following the rules of the system.
    display = models.CharField(max_length=255)

    # Indicates that this coding was chosen by a user directly -
    # i.e. off a pick list of available items (codes or displays).
    userselected = models.BooleanField()


class Meta(models.Model):
    """Abstract meta data model for Mixin

    All resources use that meta data."""

    versionId = IdField(primary_key=True)

    # this one is not genuine from FHIR, but it may be usable sometimes for auditing.
    created = models.DateTimeField(auto_created=True, editable=False)

    lastUpdated = InstantField(auto_now=True)

    profile = UriField()

    security = models.ForeignKey("Coding", on_delete=models.PROTECT, blank=True)

    class Meta:
        abstract = True


class Resource(Meta):
    id = IdField(blank=True)

    # TODO: Maybe it's better to use a OneToOneField for that
    # EVERY resource uses these metadata.
    # But maybe it's cheaper to just query for resources, without the other table "Meta"
    # meta = models.OneToOneField(Meta, on_delete=models.CASCADE)

    implicitRules = UriField(blank=True)

    # the language of the resource, either "en" or "en-US"
    language = CodeField(blank=True)
    # TODO: language choices, see http://build.fhir.org/valueset-languages.html
    # or use the django internals?


class DomainResource(Resource):
    text = NarrativeField()
    contained = models.ManyToManyField(Resource, related_name="parent_resource")


class Patient(Meta):
    pass


