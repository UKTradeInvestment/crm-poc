from unittest import mock

from django.utils import timezone

from cdms_api.base import CDMSApi
from cdms_api.utils import datetime_to_cdms_datetime


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
