from django.db import models
from django.db import transaction
from django.core.exceptions import ValidationError

from model_utils.models import TimeStampedModel

from cdms_api import api

from .utils import update_cdms_data_from_local, parse_cdms_date, \
    update_local_from_cdms_data, get_conflicting_fields


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    # migration settings, you need to override these
    CDMS_FIELD_MAPPING = {}
    CDMS_SERVICE = 'Account'

    def save_without_cdms(self, *args, **kwargs):
        super(CDMSModel, self).save(*args, **kwargs)

    def clean(self):
        super(CDMSModel, self).clean()

        cdms_data, changed = self._get_cdms_obj()
        if changed:
            # this shouldn't happen often as django 'gets' the object
            # at each request and when we get, we update as well so
            # the this conflict happens only if there's a cdms write
            # between the django get and the save (very unlikely).
            conflicting_fields = get_conflicting_fields(self, cdms_data)
            if conflicting_fields:
                raise ValidationError({
                    field: 'cdms change: {cdms}, your change: {yours}'.format(
                        cdms=conflicting_data['theirs'],
                        yours=conflicting_data['yours']
                    ) for field, conflicting_data in conflicting_fields.items()
                })

    def _get_cdms_obj(self):
        cdms_data = api.get(self.CDMS_SERVICE, self.cdms_pk)
        cdms_modified_on = parse_cdms_date(cdms_data['ModifiedOn'])

        change_delta = (cdms_modified_on - self.modified).total_seconds()

        if change_delta < -2:
            raise Exception('Django Model changed without being syncronised to CDMS, this should not happen')

        changed = change_delta > 2

        return (cdms_data, changed)

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.pk:
                # save this
                super(CDMSModel, self).save(*args, *kwargs)

                # create in cdms
                cdms_data = update_cdms_data_from_local(self, {})

                cdms_obj = api.create(self.CDMS_SERVICE, data=cdms_data)
                self.cdms_pk = cdms_obj['{service}Id'.format(service=self.CDMS_SERVICE)]
                self.__class__.objects.filter(pk=self.pk).update(cdms_pk=self.cdms_pk)
            else:
                # get from cdms
                cdms_data, changed = self._get_cdms_obj()
                if changed:
                    # should never happen if self.clean called before saving
                    raise Exception()

                # save this
                super(CDMSModel, self).save(*args, *kwargs)

                cdms_data = update_cdms_data_from_local(self, cdms_data)
                cdms_obj = api.update(self.CDMS_SERVICE, guid=self.cdms_pk, data=cdms_data)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            super(CDMSModel, self).delete(*args, **kwargs)

            api.delete(self.CDMS_SERVICE, guid=self.cdms_pk)

    def sync_from_cdms(self):
        with transaction.atomic():
            # get from cdms
            cdms_data, changed = self._get_cdms_obj()
            if not changed:
                return False

            update_local_from_cdms_data(self, cdms_data)
            self.save_without_cdms()
            api.update(self.CDMS_SERVICE, guid=self.cdms_pk, data=cdms_data)
            return True

    class Meta:
        abstract = True
