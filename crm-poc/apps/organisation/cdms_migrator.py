from django.apps import apps

from cdms_api import fields as cdms_fields

from migrator.cdms_migrator import BaseCDMSMigrator


class IdRefField(cdms_fields.BaseField):
    def to_cdms_value(self, value):
        if not value:
            return value
        return {'Id': value}

    def from_cdms_value(self, value):
        if not value:
            return value
        return value['Id']


class ObjectRefField(IdRefField):
    def __init__(self, cdms_name, fk_model):
        super(ObjectRefField, self).__init__(cdms_name)
        self.fk_model = fk_model

    def get_model(self):
        return apps.get_model(self.fk_model)

    def to_cdms_value(self, value):
        if not value:
            return value
        return super(ObjectRefField, self).to_cdms_value(value.cdms_pk)

    def from_cdms_value(self, value):
        if not value:
            return value

        cdms_pk = super(ObjectRefField, self).from_cdms_value(value)
        return self.get_model()(cdms_pk=cdms_pk)


class OrganisationMigrator(BaseCDMSMigrator):
    fields = {
        'name': cdms_fields.StringField('Name'),
        'alias': cdms_fields.StringField('optevia_Alias'),
        'uk_organisation': cdms_fields.BooleanField('optevia_ukorganisation'),
        'country': IdRefField('optevia_Country'),
        'postcode': cdms_fields.StringField('optevia_PostCode'),
        'address1': cdms_fields.StringField('optevia_Address1'),
        'city': cdms_fields.StringField('optevia_TownCity'),
        'uk_region': IdRefField('optevia_UKRegion'),
        'country_code': cdms_fields.StringField('optevia_CountryCode'),
        'area_code': cdms_fields.StringField('optevia_AreaCode'),
        'phone_number': cdms_fields.StringField('optevia_TelephoneNumber'),
        'email_address': cdms_fields.StringField('EMailAddress1'),
        'sector': IdRefField('optevia_Sector'),
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


class ContactMigrator(BaseCDMSMigrator):
    fields = {
        'first_name': cdms_fields.StringField('FirstName'),
        'last_name': cdms_fields.StringField('LastName'),
        'organisation': ObjectRefField(
            'ParentCustomerId',
            fk_model='organisation.Organisation'
        )
    }
    service = 'Contact'
