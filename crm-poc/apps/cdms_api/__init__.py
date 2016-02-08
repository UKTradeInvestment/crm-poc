from django.conf import settings

from .base import CDMSApi

if settings.IN_TESTING:
    from .utils import get_mocked_api
    api = get_mocked_api()
else:
    api = CDMSApi(
        settings.CDMS_USERNAME,
        settings.CDMS_PASSWORD,
    )
