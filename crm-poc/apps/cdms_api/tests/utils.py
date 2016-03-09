import datetime

from unittest import mock

from django.utils import timezone

from cdms_api.base import CDMSApi
from cdms_api.utils import datetime_to_cdms_datetime


def populate_data(data, service, guid=None):
    _data = dict(data)
    _data['ModifiedOn'] = _data.get('ModifiedOn', timezone.now())
    _data['CreatedOn'] = _data.get('CreatedOn', timezone.now())

    id_key = '{0}Id'.format(service)
    _data[id_key] = guid or _data.get(id_key, 'cdms-pk')

    for k, v in _data.items():
        if isinstance(v, datetime.datetime):
            _data[k] = datetime_to_cdms_datetime(v)
    return _data


def mocked_cdms_get(get_data={}):
    def internal(service, guid):
        return populate_data(get_data, service, guid)
    return internal


def mocked_cdms_create(create_data={}):
    def internal(service, data):
        return populate_data(create_data, service)
    return internal


def mocked_cdms_update(update_data={}):
    def internal(service, guid, data):
        return populate_data(update_data, service, guid)
    return internal


def mocked_cdms_list(list_data=[]):
    def internal(service, *args, **kwargs):
        return [populate_data(item, service) for item in list_data]
    return internal


def get_mocked_api():
    api = mock.MagicMock(spec=CDMSApi)

    api.create.side_effect = mocked_cdms_create()
    api.get.side_effect = mocked_cdms_get()
    api.update.side_effect = mocked_cdms_update()
    api.list.side_effect = mocked_cdms_list()
    return api
