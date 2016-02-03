import re
import datetime


def update_cdms_data_from_local(local_obj, cdms_data):
    for field in local_obj._meta.fields:
        field_name = field.name
        mapping = local_obj.CDMS_FIELD_MAPPING.get(field_name)
        if not mapping:
            continue

        cdms_field, mapping_func, _ = (mapping, (lambda x: x), None) if not isinstance(mapping, tuple) else mapping

        value = mapping_func(getattr(local_obj, field_name))

        cdms_data[cdms_field] = value
    return cdms_data


def update_local_from_cdms_data(local_obj, cdms_data):
    for field in local_obj._meta.fields:
        field_name = field.name
        mapping = local_obj.CDMS_FIELD_MAPPING.get(field_name)
        if not mapping:
            continue

        cdms_field, _, mapping_func = (mapping, None, (lambda x: x)) if not isinstance(mapping, tuple) else mapping

        value = mapping_func(cdms_data[cdms_field])

        setattr(local_obj, field_name, value)

    return local_obj


def get_conflicting_fields(local_obj, cdms_data):
    """
    Returns the list of fields conflicting between local_obj and cdms_data.
    """
    conflicting_fields = {}
    for field in local_obj._meta.fields:
        field_name = field.name
        mapping = local_obj.CDMS_FIELD_MAPPING.get(field_name)
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


def parse_cdms_date(val):
    # dates from CDMS are in UTC
    parsed_val = int(re.search('/Date\(([-+]?\d+)\)/', val).group(1))
    parsed_val = datetime.datetime.fromtimestamp(parsed_val / 1000)
    return parsed_val.replace(tzinfo=datetime.timezone.utc)
