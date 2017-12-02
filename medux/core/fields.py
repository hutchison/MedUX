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

from django.core.validators import RegexValidator
from django.db import models

import base64
from uuid import uuid4

# TODO This could be done better, especially the Validations
# see http://build.fhir.org/datatypes.html

__all__ = ["Base64TextField", "UriField", "InstantField", "CodeField", "OidField", "IdField", "MarkdownField",
           "NarrativeField"]


class Base64TextField(models.TextField):
    """A stream of bytes, base64 encoded"""

    @staticmethod
    def from_db_value(value):
        """Returns a str from the database value, which is encoded as base64 string"""
        if value is None:
            return None
        else:
            return base64.b64decode(value).decode("utf-8")

    # TODO: read only yet


class UriField(models.CharField):
    """A Uniform Resource Identifier Reference.

    This is a URI, as defined in RFC 3986:
    https://tools.ietf.org/html/rfc3986
    Note: URIs generally are case sensitive. For UUID use all lowercase letters!
    """
    # TODO: implementation
    def __init__(self, *args, **kwargs):
        # FIXME: we set this to an arbitrary 255 char string as max. could be more specific
        kwargs['max_length'] = 255
        super().__init__(*args, **kwargs)

class InstantField(models.DateTimeField):
    """An instant in time - known at least to the second and always includes a time zone.

    Note: This type is for system times, not human times."""


class CodeField(models.CharField):
    """Represents a field with a "code" that is defined elsewhere.

    Technically, a code is restricted to a string which has at least one character and
    no leading or trailing whitespace, and where there is no whitespace other than single
    spaces in the contents"""
    # TODO: should this be a ForeignKey, or an Enum?

    def __init__(self, *args, **kwargs):
        # TODO: we set this to an arbitrary 64 char string as max. Could be more specific
        kwargs['max_length'] = 64
        super().__init__(*args, **kwargs)

class OidField(UriField):
    """An OID represented as a URI"""

    def __init__(self, *args, **kwargs):
        kwargs['validators'] = [RegexValidator(
            regex='[0-2](\.[1-9]\d*)+',
            message='Given string is no OID'
        )]
        super().__init__(*args, **kwargs)


class IdField(models.CharField):
    """A field that can be used for an ID of an Object.

    Any combination of upper or lower case ASCII letters ('A'..'Z', and 'a'..'z',
    numerals ('0'..'9'), '-' and '.', with a length limit of 64 characters.
    This might be an integer, an un-prefixed OID, UUID or any other identifier
    pattern that meets these constraints."""

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 64
        kwargs['default'] = uuid4()
        super().__init__(*args, **kwargs)



class MarkdownField(models.TextField):
    """A string that *may* contain markdown syntax.

     This can be used for optional processing by a markdown presentation engine"""


# http://hl7.org/fhir/narrative-status
NARRATIVE_STATUS = (
    ("generated", "Generated"),
    ("extensions", "Extensions"),
    ("additional", "Additional"),
    ("empty", "Empty")
)


class NarrativeField(models.TextField):
    status = models.CharField(max_length=35, choices=NARRATIVE_STATUS)

    # TODO: implement a XHTMLField
    # The XHTML content SHALL NOT contain a head, a body element, external stylesheet references,
    # deprecated elements, scripts, forms, base/link/xlink, frames, iframes, objects or event related attributes
    # (e.g. onClick).This is to ensure that the content of the narrative is contained within the resource
    # and that there is no active content. Such content would introduce security issues and potentially safety
    # issues with regard to extracting text from the XHTML.
    div = models.TextField(null=False, blank=False)
