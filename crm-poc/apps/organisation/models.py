from django.db import models
from django.core.urlresolvers import reverse

from model_utils.models import TimeStampedModel

from .managers import OrganisationManager

CDMS_FIELD_MAPPING = {
    'name': 'Name',
    'alias': 'optevia_Alias',
    'uk_organisation': 'optevia_ukorganisation',
    'country': ('optevia_Country', lambda x: {'Id': x}),
    'postcode': 'optevia_PostCode',
    'address1': 'optevia_Address1',
    'uk_region': ('optevia_UKRegion', lambda x: {'Id': x}),
    'country_code': 'optevia_CountryCode',
    'area_code': 'optevia_AreaCode',
    'phone_number': 'optevia_TelephoneNumber',
    'email_address': 'EMailAddress1',
    'sector': ('optevia_Sector', lambda x: {'Id': x}),
}


class Organisation(TimeStampedModel):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255, blank=True)

    uk_organisation = models.BooleanField(default=True)
    country = models.CharField(
        max_length=255,
        choices=(
            ('80756b9a-5d95-e211-a939-e4115bead28a', 'United Kingdom'),
        )
    )
    postcode = models.CharField(max_length=255)
    address1 = models.CharField(max_length=255)
    uk_region = models.CharField(
        max_length=255,
        choices=(
            ('874cd12a-6095-e211-a939-e4115bead28a', 'London'),
        )
    )

    country_code = models.CharField(max_length=255)
    area_code = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=255)

    email_address = models.CharField(max_length=255)

    sector = models.CharField(
        max_length=255,
        choices=(
            ('a538cecc-5f95-e211-a939-e4115bead28a', 'Food & Drink'),
        )
    )

    cdms_pk = models.CharField(max_length=255, blank=True)

    objects = OrganisationManager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('organisation:update', args=[str(self.id)])

    def save(self, *args, **kwargs):
        create = not self.pk

        from cdms_api import api
        import datetime
        import re

        def update_cdms_data_from_local(organisation, data):
            cdms_data = dict(data)
            for field in organisation._meta.fields:
                field_name = field.name
                mapping = CDMS_FIELD_MAPPING.get(field_name)
                if not mapping:
                    continue

                cdms_field, mapping_func = (mapping, (lambda x: x)) if not isinstance(mapping, tuple) else mapping

                value = mapping_func(getattr(organisation, field_name))

                cdms_data[cdms_field] = value
            return cdms_data

        if create:
            # save this
            super(Organisation, self).save(*args, *kwargs)

            # create in cdms
            cdms_data = update_cdms_data_from_local(self, {})

            cdms_organisation = api.create('Account', data=cdms_data)
            self.cdms_pk = cdms_organisation['AccountId']
            self.__class__.objects.filter(pk=self.pk).update(cdms_pk=self.cdms_pk)
        else:
            # get from cdms
            cdms_data = api.get('Account', self.cdms_pk)

            # dates from CDMS are in UTC
            cdms_modified_on = int(re.search('/Date\(([-+]?\d+)\)/', cdms_data['ModifiedOn']).group(1))
            cdms_modified_on = datetime.datetime.fromtimestamp(cdms_modified_on / 1000)
            cdms_modified_on = cdms_modified_on.replace(tzinfo=datetime.timezone.utc)

            last_self_modified_on = self.modified

            if abs(cdms_modified_on - last_self_modified_on).total_seconds() > 2:  # if > 2 secs
                # TODO: somebody modified CDMS record after getting this obj
                # we need to deal with it somehow
                raise Exception()

            # save this
            super(Organisation, self).save(*args, *kwargs)

            del cdms_data['optevia_LastVerified']
            del cdms_data['ModifiedOn']
            del cdms_data['CreatedOn']

            cdms_data = update_cdms_data_from_local(self, cdms_data)
            cdms_organisation = api.update('Account', guid=self.cdms_pk, data=cdms_data)
