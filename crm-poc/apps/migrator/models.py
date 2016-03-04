from django.db import models, transaction

from core.lib_models import TimeStampedModel


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    cdms_migrator = None  # should be subclass of migrator.cdms_migrator.BaseCDMSMigrator

    def __init__(self, *args, **kwargs):
        super(CDMSModel, self).__init__(*args, **kwargs)
        self._cdms_skip = False

    def save(self, *args, **kwargs):
        # a bit hacky but it makes things work :-P
        original_cdms_skip = self._cdms_skip
        self._cdms_skip = kwargs.pop('skip_cdms', self._cdms_skip)
        try:
            ret = super(CDMSModel, self).save(*args, **kwargs)
        finally:
            self._cdms_skip = original_cdms_skip

        return ret

    def _do_insert(self, manager, using, fields, update_pk, raw):
        if self._cdms_skip:
            manager = manager.skip_cdms()
        return super(CDMSModel, self)._do_insert(manager, using, fields, update_pk, raw)

    def _do_update(self, base_qs, using, pk_val, values, update_fields, forced_update):
        if self._cdms_skip:
            base_qs = base_qs.skip_cdms()
        return super(CDMSModel, self)._do_update(base_qs, using, pk_val, values, update_fields, forced_update)

    def _do_delete_cdms_obj(self):
        """
        Private method which only deletes the cdms object. Not meant to be used publicly.
        """
        from .query import DeleteQuery

        assert self.cdms_pk, \
            "%s object can't be deleted because its cdms_pk attribute is not set." % self._meta.object_name

        query = DeleteQuery(self.__class__)
        query.set_cdms_pk(self.cdms_pk)
        query.get_compiler().execute()

    def delete(self, *args, **kwargs):
        original_cdms_skip = self._cdms_skip
        self._cdms_skip = kwargs.pop('skip_cdms', self._cdms_skip)

        try:
            with transaction.atomic():
                ret = super(CDMSModel, self).delete(*args, **kwargs)

                if not self._cdms_skip:
                    self._do_delete_cdms_obj()
        finally:
            self._cdms_skip = original_cdms_skip

        return ret

    class Meta:
        abstract = True
