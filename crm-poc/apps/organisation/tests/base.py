from ..models import Organisation
from ..models import COUNTRY_CHOICES, UK_REGION_CHOICES, SECTOR_CHOICES


def get_sample_organisation():
    return Organisation(
        name='name',
        alias='alias',
        uk_organisation=True,
        country=COUNTRY_CHOICES[0][0],
        postcode='postcode',
        address1='address1',
        city='city',
        uk_region=UK_REGION_CHOICES[0][0],
        country_code='country code',
        area_code='area code',
        phone_number='phone number',
        email_address='email address',
        sector=SECTOR_CHOICES[0][0]
    )


def get_sample_cdms_organisation(data={}):
    defaults = {
        'EMailAddress1': 'email address',
        'optevia_AreaCode': 'area code',
        'optevia_PAFOverride': True,
        'optevia_ukorganisation': True,
        'optevia_PostCode': 'postcode',
        'optevia_UKRegion': {'Id': UK_REGION_CHOICES[0][0]},
        'optevia_Alias': 'alias',
        'optevia_Sector': {'Id': SECTOR_CHOICES[0][0]},
        'optevia_Address1': 'address1',
        'optevia_TelephoneNumber': 'phone number',
        'Name': 'name',
        'optevia_Country': {'Id': COUNTRY_CHOICES[0][0]},
        'optevia_TownCity': 'city',
        'optevia_CountryCode': 'country code'
    }
    defaults.update(data)
    return defaults
