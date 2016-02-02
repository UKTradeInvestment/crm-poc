from django.db import models
from django.core.urlresolvers import reverse

from .managers import OrganisationManager


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

        return super(Organisation, self).save(*args, *kwargs)
