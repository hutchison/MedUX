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

from .fields import *

__author__ = "Christian González <christian.gonzalez@nerdocs.at>"


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


# Extension
class Period(models.Model):
    """A time period defined by a start and end date/time.

    If the start element is missing, the start of the period is not known.
    If the end element is missing, it means that the period is ongoing, or the start may be in the past,
    and the end date in the future, which means that period is expected/planned to end at the specified time
    """
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)


class Meta(models.Model):
    """Abstract meta data model for Mixin

    All resources use that meta data."""

    versionId = IdField(primary_key=True)

    # this one is not genuine from FHIR, but it may be usable sometimes for auditing.
    created = models.DateTimeField(auto_created=True, editable=False)

    lastUpdated = InstantField(auto_now=True)

    profile = models.ManyToManyField("StructureDefinition")

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


# http://hl7.org/fhir/publication-status
# FIXME: implement expansion automatically, in code
PUBLICATION_STATUS = (
    ("draft", "Draft"),
    ("active", "Active"),
    ("retired", "Retired"),
    ("unknown", "Unknown"),
)


class Element(models.Model):
    """ The base definition for all elements contained inside a resource.

    All elements, whether defined as a Data Type (including primitives) or as part of a resource structure,
    have this base content:

    * Extensions
    * an internal id
    """

    # This field originally is named "extension". This causes some problemswith name clashing
    # So, as it's a ManyToManyField anyway, we renamed it to "extensions"
    extensions = models.ManyToManyField("Extension", related_name="extends")

    # class Meta:
    #    abstract = True


class Extension(Element):

    # SHALL be a URL, not a URN (e.g. not an OID or a UUID),
    url = UriField()

    # FIXME: this field in reality should be more flexible.
    # see http://build.fhir.org/extensibility.html#Extension
    # value = models.CharField(max_length=255, blank=True)

#    class Meta:
#        abstract = True


class ContactPoint(Element):
    """Details for all kinds of technology-mediated contact points for a person or organization

    This includes telephone, email, etc. """

    # links to ContactPointSystem
    # http://hl7.org/fhir/ValueSet/contact-point-system
    system = CodeField("ContactPointSystem", blank=True)
    value = models.CharField(max_length=255, blank=True)

    # links to ContactPointUse
    # http://hl7.org/fhir/ValueSet/contact-point-use
    use = CodeField("ContactPointUse", blank=True)
    rank = models.PositiveIntegerField(default=0)
    period = models.ForeignKey(Period, on_delete=models.PROTECT, null=True)


class ContactDetail(Element):
    name = models.CharField(max_length=255)
    telecom = models.ManyToManyField(ContactPoint)


class StructureDefinition(DomainResource):
    url = UriField()
    identifier = models.ManyToManyField("Identifier")
    version = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255)
    title = models.CharField(max_length=255, blank=True)

    # http://hl7.org/fhir/ValueSet/publication-status
    status = CodeField(choices=PUBLICATION_STATUS)

    experimental = models.BooleanField()
    date = models.DateTimeField(null=True)
    publisher = models.CharField(blank=True, max_length=255)

    contact = models.ManyToManyField("ContactDetail")
    description = MarkdownField()
    use_context = models.ManyToManyField("UsageContext")


# http://hl7.org/fhir/identifier-use
# FIXME: implement expansion automatically, as ValueSet
IDENTIFIER_USE = (
    ("usual", "Usual"),
    ("official", "Official"),
    ("temp", "Temp"),
    ("secondary", "Secondary"),
    ("old", "Old"),
)


class Identifier(models.Model):
    """A numeric or alphanumeric string that is associated with a single object or entity within a given system.

    Typically, identifiers are used to connect content in resources to external content available in other
    frameworks or protocols. Identifiers are associated with objects, and may be changed or retired due to
    human or system process and errors."""

    use = CodeField(choices=IDENTIFIER_USE)
    type = models.ForeignKey("CodeableConcept", null=True, on_delete=models.SET_NULL)

    # FIXME: this is an URI in FHIR
    # http://build.fhir.org/datatypes.html#Identifier
    #
    # * http://hl7.org/fhir/sid/us-ssn for United States Social Security Number (SSN) values
    # * http://ns.electronichealth.net.au/id/hi/ihi/1.0 for Australian Individual Healthcare Identifier (IHI) numbers
    # * urn:ietf:rfc:3986 for when the value of the identifier is itself a globally unique URI
    # This could link to the Austrian SVNR system as well.

    system = UriField(null=False)

    # http://build.fhir.org/datatypes-definitions.html#Identifier.value
    # The portion of the identifier typically relevant to the user and which is unique within the context of the system.
    value = models.CharField
    period = models.ForeignKey(Period, null=True, on_delete=models.SET_NULL)

    assigner = ReferenceField("Organisation", null=True, on_delete=models.SET_NULL, related_name="asignee")


class Organisation(DomainResource):
    # The organization SHALL at least have a name or an id, and possibly more than one
    identifier = models.ManyToManyField(Identifier)


class Reference(Element):
    # A reference to a location at which the other resource is found.
    references = models.CharField(max_length=255, blank=True)
    identifier = models.ForeignKey("Identifier", null=True, on_delete=models.CASCADE)
    display = models.CharField(max_length=255, blank=True)

    # TODO: At least one of reference, identifier and display SHALL be present (unless an extension is provided).

    def validate_unique(self, exclude=None):
        pass


class CodeableConcept(models.Model):
    coding = models.ManyToManyField(Coding)
    text = models.TextField()


class UsageContext(Element):
    code = CodeField("UsageContextType", null=False)
    value = CodeField(CodeableConcept)


class ValueSet(DomainResource):
    url = UriField()

    # TODO: check if SET_NULL is appropriate here
    identifier = models.ManyToManyField(Identifier)
    version = models.CharField(max_length=255, blank=True)
    name = models.CharField(max_length=255, blank=True)
    title = models.CharField(max_length=255, blank=True)
    status = CodeField("PublicationStatus")
    experimental = models.BooleanField(default=False)
    date = models.DateTimeField()
    publisher = models.CharField(max_length=255, blank=True)
    contact = models.ForeignKey(ContactDetail, null=True, on_delete=models.SET_NULL)
    descripttion = MarkdownField()
    use_context = models.ManyToManyField(UsageContext)

    # http://hl7.org/fhir/ValueSet/jurisdiction
    # A legal or geographic region in which the value set is intended to be used.
    jurisdiction = models.ManyToManyField(CodeableConcept)

    # If this is set to 'true', then no new versions of the content logical definition can be created.
    # Note: Other metadata might still change.
    immutable = models.BooleanField(default=False)

    # Explanation of why this value set is needed and why it has been designed as it has.
    purpose = MarkdownField()

    # A copyright statement relating to the value set and/or its contents.
    # Copyright statements are generally legal restrictions on the use and publishing of the value set.
    copyright = MarkdownField()

    extensible = models.BooleanField(default=False)


class HumanName(Element):
    # https://www.hl7.org/fhir/valueset-name-use.html
    use = CodeField("NameUse")

    # the entire name, as it should be represented
    text = models.CharField(max_length=255)

    family = models.CharField(max_length=255)

    # space separated strings
    # Initials may be used in place of the full name if that is all that is recorded
    given = models.CharField(max_length=255)


class Address(Element):
    """An address expressed using postal conventions (as opposed to GPS or other location definition formats).
    This data type may be used to convey addresses for use in delivering mail as well as for visiting
    locations which might not be valid for mail delivery.
    There are a variety of postal address formats defined around the world.
    """
    use = CodeField("AddressUse")
    type = CodeField("AddressType")

    # The *text* element specifies the entire address as it should be represented.
    # This may be provided instead of or as well as the specific parts.
    # Applications updating an address SHALL ensure either that the text and the parts are in agreement,
    # or that only one of the two is present.
    text = models.CharField(max_length=255)

    # This component contains the house number, apartment number, street name, street direction,
    # P.O. Box number, delivery hints, and similar address information.
    line = models.CharField(max_length=255)

    # The name of the city, town, village or other community or delivery center.
    city = models.CharField(max_length=255)

    # The name of the administrative area (county).
    # District is sometimes known as county, but in some regions 'county' is used in place of city (municipality),
    # so county name should be conveyed in city instead.
    district = models.CharField(max_length=255)

    state = models.CharField(max_length=255)

    # = zip
    postalCode = models.CharField(max_length=10)

    # Country - a nation as commonly understood or generally accepted.
    # ISO 3166 3 letter codes can be used in place of a full country name.
    country = models.CharField(max_length=255)

    period = models.ForeignKey(Period, on_delete=models.SET_NULL, null=True)


class Attachment(models.Model):
    """For referring to data content defined in other formats."""

    # Identifies the type of the data in the attachment and allows a method to be chosen to interpret
    # or render the data. Includes mime type parameters such as charset where appropriate.
    contentType = CodeField("MimeType", blank=True)

    # The human language of the content. The value can be any valid value according to BCP 47.
    language = CodeField("Common Languages", blank=True)

    # The actual data of the attachment - a sequence of bytes. In XML, represented using base64.
    data = Base64TextField(blank=True)

    # An alternative location where the data can be accessed.
    url = UriField(blank=True)
    # If both data and url are provided, the url SHALL point to the same content as the data contains.

    # The number of bytes of data that make up this attachment (before base64 encoding, if that is done).
    size = models.PositiveIntegerField(blank=True)

    # The calculated hash of the data using SHA-1. Represented using base64.
    hash = Base64TextField(blank=True)

    # A label or set of text to display in place of the data.
    title = models.CharField(max_length=255, blank=True)

    # The date that the attachment was first created.
    creation = models.DateTimeField(auto_created=True)

    def __str__(self):
        return self.title if self.title else self.data


class Patient(models.Model):
    identifier = models.ManyToManyField(Identifier)
    active = models.BooleanField()
    name = models.ManyToManyField(HumanName)
    telecom = models.ManyToManyField(ContactPoint)
    gender = CodeField("AdministrativeGender")
    birthdate = models.DateField(blank=True)

    # if this field is blank, the REST API should return boolean "False"
    # https://www.hl7.org/fhir/patient-definitions.html#Patient.deceased_x_
    deceased = models.DateTimeField(blank=True)
    address = models.ManyToManyField(Address)

    maritialStatus = CodeableConcept("MaritialStatus")

    # Indicates whether the patient is part of a multiple (bool) or indicates the actual birth order (integer).
    # FIXME we use 0 as bool/False here, because [x] is difficult to implement in Django
    multipleBirth = models.IntegerField()

    photo = models.ForeignKey(Attachment, on_delete=models.SET_NULL, null=True)

    # FIXME - Reference to Organisation OR Practitioner is not really implemented.
    # don't know how to do here yet.
    generalPractitioner = ReferenceField("Organization|Practitioner", on_delete=models.SET_NULL, null=True,
                                         related_name="+")
    managingOrganisation = ReferenceField(Organisation, on_delete=models.SET_NULL, null=True,
                                          related_name="+")
