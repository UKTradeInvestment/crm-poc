from migrator.cdms_migrator import BaseCDMSMigrator


class OrganisationMigrator(BaseCDMSMigrator):
    fields = {
        'name': 'Name',
        'alias': 'optevia_Alias',
        'uk_organisation': 'optevia_ukorganisation',
        'country': ('optevia_Country', lambda x: {'Id': x}, lambda x: x['Id']),
        'postcode': 'optevia_PostCode',
        'address1': 'optevia_Address1',
        'uk_region': ('optevia_UKRegion', lambda x: {'Id': x}, lambda x: x['Id']),
        'country_code': 'optevia_CountryCode',
        'area_code': 'optevia_AreaCode',
        'phone_number': 'optevia_TelephoneNumber',
        'email_address': 'EMailAddress1',
        'sector': ('optevia_Sector', lambda x: {'Id': x}, lambda x: x['Id']),
    }
    service = 'Account'
