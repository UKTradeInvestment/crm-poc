from django.db import models

from model_utils.models import TimeStampedModel


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    cdms_migrator = None  # should be subclass of migrator.cdms_migrator.BaseCDMSMigrator

    def __init__(self, *args, **kwargs):
        super(CDMSModel, self).__init__(*args, **kwargs)
        self._cdms_skip = False

    def save(self, *args, **kwargs):
        # a bit hacky but it makes things work :-P
        original_cdms_skip = self._cdms_skip
        self._cdms_skip = kwargs.pop('cdms_skip', False)
        try:
            ret = super(CDMSModel, self).save(*args, **kwargs)
        finally:
            self._cdms_skip = original_cdms_skip

        return ret

    def _do_insert(self, manager, using, fields, update_pk, raw):
        if self._cdms_skip:
            manager = manager.mark_as_cdms_skip()
        return super(CDMSModel, self)._do_insert(manager, using, fields, update_pk, raw)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        if self._cdms_skip:
            base_qs = base_qs.mark_as_cdms_skip()
        return super(CDMSModel, self)._do_update(base_qs, using, pk_val, values, update_fields, forced_update)

    class Meta:
        abstract = True
