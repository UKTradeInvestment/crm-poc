from contextlib import ContextDecorator

from django.db import models, transaction

from core.lib_models import TimeStampedModel


class override_skip_cdms(ContextDecorator):
    """
    Context Manager used to temporarily override the _cdms_skip
    class attribute with the `overriding_skip_cdms` given.
    """
    def __init__(self, obj, overriding_skip_cdms):
        self.obj = obj
        self.overriding_skip_cdms = overriding_skip_cdms

    def __enter__(self):
        self.original_skip_cdms = self.obj._cdms_skip
        self.obj._cdms_skip = self.overriding_skip_cdms
        return self

    def __exit__(self, *exc):
        self.obj._cdms_skip = self.original_skip_cdms
        del self.original_skip_cdms
        return False


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    cdms_migrator = None  # should be subclass of migrator.cdms_migrator.BaseCDMSMigrator

    def __init__(self, *args, **kwargs):
        super(CDMSModel, self).__init__(*args, **kwargs)
        self._cdms_skip = False

    def save(self, *args, **kwargs):
        overriding_skip_cdms = kwargs.pop('skip_cdms', self._cdms_skip)
        with override_skip_cdms(self, overriding_skip_cdms):
            return super(CDMSModel, self).save(*args, **kwargs)

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
        ret = None
        overriding_skip_cdms = kwargs.pop('skip_cdms', self._cdms_skip)
        with override_skip_cdms(self, overriding_skip_cdms):
            with transaction.atomic():
                ret = super(CDMSModel, self).delete(*args, **kwargs)

                if not self._cdms_skip:
                    self._do_delete_cdms_obj()

        return ret

    class Meta:
        abstract = True
