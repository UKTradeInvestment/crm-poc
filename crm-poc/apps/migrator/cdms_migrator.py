from django.db import models

from .exceptions import NotMappingFieldException
from .utils import parse_cdms_date


class BaseCDMSMigrator(object):
    fields = {}
    service = None

    def get_cdms_pk(self, cdms_data):
        return cdms_data['{service}Id'.format(service=self.service)]

    def has_cdms_obj_changed(self, local_obj, cdms_data):
        cdms_modified_on = parse_cdms_date(cdms_data['ModifiedOn'])
        cdms_created_on = parse_cdms_date(cdms_data['CreatedOn'])

        change_delta = (cdms_modified_on - local_obj.modified).total_seconds()

        if change_delta < -2:
            raise Exception('Django Model changed without being syncronised to CDMS, this should not happen')

        changed = change_delta > 2
        return changed, cdms_modified_on, cdms_created_on

    def get_fields_mapping(self, field_name):
        mapping = self.fields.get(field_name)
        if not mapping:
            raise NotMappingFieldException(
                'No mapping found for field {field}'.format(field=field_name)
            )

        return (mapping, (lambda x: x), (lambda x: x)) if not isinstance(mapping, tuple) else mapping

    def update_cdms_data_from_local(self, local_obj, cdms_data):
        values = [
            (field, getattr(local_obj, field.name)) for field in local_obj._meta.fields
        ]
        return self.update_cdms_data_from_values(values, cdms_data)

    def update_cdms_data_from_values(self, values, cdms_data):
        for field, value in values:
            field_name = field.name
            try:
                cdms_field, mapping_func, _ = self.get_fields_mapping(field_name)
            except NotMappingFieldException:
                continue

            value = mapping_func(value)
            cdms_data[cdms_field] = value
        return cdms_data

    def parse_cdms_value(self, local_field, cdms_value):
        if isinstance(local_field, models.CharField) and not cdms_value:
            return ''
        return cdms_value

    def update_local_from_cdms_data(self, local_obj, cdms_data, cdms_known_related_objects={}):
        for field in local_obj._meta.fields:
            field_name = field.name
            try:
                cdms_field, _, mapping_func = self.get_fields_mapping(field_name)
            except NotMappingFieldException:
                continue

            raw_value = mapping_func(cdms_data[cdms_field])
            value = self.parse_cdms_value(field, raw_value)
            if field_name in cdms_known_related_objects:
                related_obj = cdms_known_related_objects.get(field_name, {}).get(value.cdms_pk)

                if related_obj:
                    value = related_obj

            setattr(local_obj, field_name, value)

        return local_obj

    def get_conflicting_fields(self, local_obj, cdms_data):
        """
        Returns the list of fields conflicting between local_obj and cdms_data.
        """
        conflicting_fields = {}
        for field in local_obj._meta.fields:
            field_name = field.name
            mapping = self.fields.get(field_name)
            if not mapping:
                continue

            cdms_field, _, mapping_func = (mapping, None, (lambda x: x)) if not isinstance(mapping, tuple) else mapping
            cdms_value = mapping_func(cdms_data[cdms_field])
            local_value = getattr(local_obj, field_name)

            if cdms_value != local_value:
                conflicting_fields[field_name] = {
                    'theirs': cdms_value,
                    'yours': local_value
                }
        return conflicting_fields
