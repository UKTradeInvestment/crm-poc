import time
from unittest import mock

from django.utils import timezone

from .base import CDMSApi


def mocked_cdms_get(service, guid):
    return {
        'ModifiedOn': '/Date({dt})/'.format(
            dt=int(time.mktime(timezone.now().timetuple()) * 1000)
        )
    }


def mocked_cdms_create(service, data):
    return {
        '{service}Id'.format(service=service): 'new cdms pk'
    }


def get_mocked_api():
    api = mock.MagicMock(spec=CDMSApi)

    api.create.side_effect = mocked_cdms_create
    api.get.side_effect = mocked_cdms_get
    return api
