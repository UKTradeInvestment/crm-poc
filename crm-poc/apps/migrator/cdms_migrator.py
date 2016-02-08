from .exceptions import NotMappingFieldException


class BaseCDMSMigrator(object):
    fields = {}
    service = None

    def get_fields_mapping(self, field_name):
        mapping = self.fields.get(field_name)
        if not mapping:
            raise NotMappingFieldException()

        return (mapping, (lambda x: x), (lambda x: x)) if not isinstance(mapping, tuple) else mapping

    def update_cdms_data_from_local(self, local_obj, cdms_data):
        for field in local_obj._meta.fields:
            field_name = field.name
            try:
                cdms_field, mapping_func, _ = self.get_fields_mapping(field_name)
            except NotMappingFieldException:
                continue

            value = mapping_func(getattr(local_obj, field_name))

            cdms_data[cdms_field] = value
        return cdms_data

    def update_local_from_cdms_data(self, local_obj, cdms_data):
        for field in local_obj._meta.fields:
            field_name = field.name
            try:
                cdms_field, _, mapping_func = self.get_fields_mapping(field_name)
            except NotMappingFieldException:
                continue

            value = mapping_func(cdms_data[cdms_field])

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
