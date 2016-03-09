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


def mocked_cdms_create(modified_on=None, cdms_id='new cdms pk', create_data={}):
    def internal(service, data):
        modified = modified_on or timezone.now()
        defaults = {
            '{service}Id'.format(service=service): cdms_id,
            'CreatedOn': datetime_to_cdms_datetime(modified),
            'ModifiedOn': datetime_to_cdms_datetime(modified),
        }
        defaults.update(create_data)
        return defaults
    return internal


def mocked_cdms_update(modified_on=None, update_data={}):
    def internal(service, guid, data):
        modified = modified_on or timezone.now()
        defaults = {
            'CreatedOn': datetime_to_cdms_datetime(modified),
            'ModifiedOn': datetime_to_cdms_datetime(modified),
        }
        defaults.update(update_data)
        return defaults
    return internal


def get_mocked_api():
    api = mock.MagicMock(spec=CDMSApi)

    api.create.side_effect = mocked_cdms_create()
    api.get.side_effect = mocked_cdms_get()
    api.update.side_effect = mocked_cdms_update()
    return api
