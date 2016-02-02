from django.conf import settings

from .base import CDMSApi

api = CDMSApi(
    settings.CDMS_USERNAME,
    settings.CDMS_PASSWORD,
)
