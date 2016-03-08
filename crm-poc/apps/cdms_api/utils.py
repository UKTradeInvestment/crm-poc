import re
import time
import datetime
from unittest import mock

from django.utils import timezone

from .base import CDMSApi


def mocked_cdms_get(modified_on=None, get_data={}):
    def internal(service, guid):
        modified = modified_on or timezone.now()
        defaults = {
            'CreatedOn': datetime_to_cdms_datetime(modified),
            'ModifiedOn': datetime_to_cdms_datetime(modified),
        }
        defaults.update(get_data)
        return defaults
    return internal


def mocked_cdms_create(create_data={}):
    def internal(service, data):
        defaults = {
            '{service}Id'.format(service=service): 'new cdms pk'
        }
        defaults.update(create_data)
        return defaults
    return internal


def get_mocked_api():
    api = mock.MagicMock(spec=CDMSApi)

    api.create.side_effect = mocked_cdms_create()
    api.get.side_effect = mocked_cdms_get
    return api


def cdms_datetime_to_datetime(val):
    # dates from CDMS are in UTC
    parsed_val = int(re.search('/Date\(([-+]?\d+)\)/', val).group(1))
    parsed_val = datetime.datetime.fromtimestamp(parsed_val / 1000)
    return parsed_val.replace(tzinfo=datetime.timezone.utc)


def datetime_to_cdms_datetime(val):
    return '/Date({0})/'.format(int(time.mktime(val.timetuple()) * 1000))
