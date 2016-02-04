from migrator.cdms_migrator import BaseCDMSMigrator


class OrganisationMigrator(BaseCDMSMigrator):
    fields = {
        'name': 'Name',
        'alias': 'optevia_Alias',
        'uk_organisation': 'optevia_ukorganisation',
        'country': ('optevia_Country', lambda x: {'Id': x}, lambda x: x['Id']),
        'postcode': 'optevia_PostCode',
        'address1': 'optevia_Address1',
        'city': 'optevia_TownCity',
        'uk_region': ('optevia_UKRegion', lambda x: {'Id': x}, lambda x: x['Id']),
        'country_code': 'optevia_CountryCode',
        'area_code': 'optevia_AreaCode',
        'phone_number': 'optevia_TelephoneNumber',
        'email_address': 'EMailAddress1',
        'sector': ('optevia_Sector', lambda x: {'Id': x}, lambda x: x['Id']),
    }
    service = 'Account'

    def update_cdms_data_from_local(self, local_obj, cdms_data):
        """
        Add PAFOverride value to cdms_data.
        """
        cdms_data = super(OrganisationMigrator, self).update_cdms_data_from_local(
            local_obj, cdms_data
        )

        if cdms_data:
            cdms_data['optevia_PAFOverride'] = True
        return cdms_data
