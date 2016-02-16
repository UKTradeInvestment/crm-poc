import time
from unittest import mock

from django.utils import timezone

from .base import CDMSApi


def mocked_cdms_get(modified_on=None, get_data={}):
    def internal(service, guid):
        modified = modified_on or timezone.now()
        defaults = {
            'ModifiedOn': '/Date({dt})/'.format(
                dt=int(time.mktime(modified.timetuple()) * 1000)
            ),
            'CreatedOn': '/Date({dt})/'.format(
                dt=int(time.mktime(modified.timetuple()) * 1000)
            )
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
