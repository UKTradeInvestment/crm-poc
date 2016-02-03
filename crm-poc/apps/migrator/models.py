from django.db import models

from model_utils.models import TimeStampedModel

from cdms_api import api

from .utils import update_cdms_data_from_local, parse_cdms_date, \
    update_local_from_cdms_data


class CDMSModel(TimeStampedModel):
    cdms_pk = models.CharField(max_length=255, blank=True)

    # migration settings, you need to override these
    CDMS_FIELD_MAPPING = {}
    CDMS_SERVICE = 'Account'

    def save_without_cdms(self, *args, **kwargs):
        super(CDMSModel, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
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
            cdms_data = api.get(self.CDMS_SERVICE, self.cdms_pk)
            cdms_modified_on = parse_cdms_date(cdms_data['ModifiedOn'])

            if abs(cdms_modified_on - self.modified).total_seconds() > 2:  # if > 2 secs
                # TODO: somebody modified CDMS record after getting this obj
                # we need to deal with it somehow
                raise Exception()

            # save this
            super(CDMSModel, self).save(*args, *kwargs)

            cdms_data = update_cdms_data_from_local(self, cdms_data)
            cdms_obj = api.update(self.CDMS_SERVICE, guid=self.cdms_pk, data=cdms_data)

    def sync_from_cdms(self):
        # get from cdms
        cdms_data = api.get(self.CDMS_SERVICE, self.cdms_pk)
        cdms_modified_on = parse_cdms_date(cdms_data['ModifiedOn'])

        # check if cdms was changed since last save
        if (cdms_modified_on - self.modified).total_seconds() <= 2:
            return False

        update_local_from_cdms_data(self, cdms_data)
        self.save_without_cdms()
        api.update(self.CDMS_SERVICE, guid=self.cdms_pk, data=cdms_data)

    class Meta:
        abstract = True
