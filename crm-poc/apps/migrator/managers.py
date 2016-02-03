from django.db import models


class CDMSQuerySet(models.QuerySet):
    def get(self, *args, **kwargs):
        obj = super(CDMSQuerySet, self).get(*args, **kwargs)
        obj.sync_from_cdms()
        return obj
