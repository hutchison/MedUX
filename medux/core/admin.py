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

from django.contrib import admin
from medux.core.models import *


admin.site.register(Resource)
admin.site.register(DomainResource)
admin.site.register(Coding)
admin.site.register(Period)
admin.site.register(StructureDefinition)
admin.site.register(Identifier)
admin.site.register(ValueSet)
admin.site.register(ContactDetail)
admin.site.register(ContactPoint)
admin.site.register(Extension)
