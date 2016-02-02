from django.db import models
from django.core.urlresolvers import reverse

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


class Organisation(models.Model):
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
        super(Organisation, self).save(*args, *kwargs)

        if create:
            # create in cdms
            from cdms_api import api

            data = {}
            for field in self._meta.fields:
                field_name = field.name
                mapping = CDMS_FIELD_MAPPING.get(field_name)
                if not mapping:
                    continue

                cdms_field, mapping_func = (mapping, (lambda x: x)) if not isinstance(mapping, tuple) else mapping

                value = mapping_func(getattr(self, field_name))

                data[cdms_field] = value

            result = api.create('Account', data=data)['d']
            self.cdms_pk = result['AccountId']
            self.__class__.objects.filter(pk=self.pk).update(cdms_pk=self.cdms_pk)
