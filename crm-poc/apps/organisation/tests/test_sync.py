from unittest import mock
from model_mommy import mommy
from django.test.testcases import TransactionTestCase

from cdms_api.utils import mocked_cdms_create, mocked_cdms_get

from ..models import Organisation
from ..models import COUNTRY_CHOICES, UK_REGION_CHOICES, SECTOR_CHOICES


class BaseOrgSyncTestCase(TransactionTestCase):
    @mock.patch('migrator.models.api')
    @mock.patch('migrator.query.cdms_conn')
    def __call__(self, result, mocked_cdms_conn, mocked_api, *args, **kwargs):
        mocked_api.create.side_effect = mocked_cdms_create
        mocked_api.get.side_effect = mocked_cdms_get
        self.mocked_api = mocked_api

        mocked_cdms_conn.create.side_effect = mocked_cdms_create
        mocked_cdms_conn.get.side_effect = mocked_cdms_get
        self.mocked_cdms_conn = mocked_cdms_conn
        super(BaseOrgSyncTestCase, self).__call__(result, *args, **kwargs)


class CreateTestCase(BaseOrgSyncTestCase):
    def get_org_data(self):
        obj = Organisation(
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

        cdms_data = {
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
        return obj, cdms_data

    def test_create_success(self):
        obj, cdms_data = self.get_org_data()

        self.assertEqual(Organisation.objects.count(), 0)
        obj.save()
        self.assertEqual(Organisation.objects.count(), 1)

        # assert cdms call
        self.assertEqual(self.mocked_cdms_conn.create.call_count, 1)
        service = self.mocked_cdms_conn.create.call_args[0][0]
        data = self.mocked_cdms_conn.create.call_args[1]['data']
        self.assertEqual(service, 'Account')
        self.assertDictEqual(data, cdms_data)

        obj = obj.__class__.objects.get(pk=obj.pk)
        self.assertEqual(obj.cdms_pk, 'new cdms pk')

    def test_create_failure(self):
        self.mocked_cdms_conn.create.side_effect = Exception

        obj, cdms_data = self.get_org_data()

        self.assertEqual(Organisation.objects.count(), 0)
        self.assertRaises(Exception, obj.save)
        self.assertEqual(Organisation.objects.count(), 0)


class UpdateTestCase(BaseOrgSyncTestCase):

    def test_update_success(self):
        obj = mommy.make(Organisation)
        self.mocked_cdms_conn.reset_mock()

        self.assertEqual(Organisation.objects.count(), 1)
        obj.name = 'Updated name'
        obj.save()
        self.assertEqual(Organisation.objects.count(), 1)

        # assert cdms call
        self.assertEqual(self.mocked_cdms_conn.update.call_count, 1)

        service = self.mocked_cdms_conn.update.call_args[0][0]
        guid = self.mocked_cdms_conn.update.call_args[1]['guid']
        data = self.mocked_cdms_conn.update.call_args[1]['data']

        self.assertEqual(service, 'Account')
        self.assertEqual(guid, obj.cdms_pk)
        self.assertEqual(data['Name'], obj.name)

    def test_update_failure(self):
        self.mocked_cdms_conn.update.side_effect = Exception

        obj = mommy.make(Organisation)

        self.assertEqual(Organisation.objects.count(), 1)
        self.assertRaises(Exception, obj.save)
        self.assertEqual(Organisation.objects.count(), 1)


class DeleteTestCase(BaseOrgSyncTestCase):

    def test_delete_success(self):
        obj = mommy.make(Organisation)

        self.assertEqual(Organisation.objects.count(), 1)
        obj.delete()
        self.assertEqual(Organisation.objects.count(), 0)

        # assert cdms call
        self.assertEqual(self.mocked_api.delete.call_count, 1)

        service = self.mocked_api.delete.call_args[0][0]
        guid = self.mocked_api.delete.call_args[1]['guid']

        self.assertEqual(service, 'Account')
        self.assertEqual(guid, obj.cdms_pk)

    def test_delete_failure(self):
        self.mocked_api.delete.side_effect = Exception

        obj = mommy.make(Organisation)

        self.assertEqual(Organisation.objects.count(), 1)
        self.assertRaises(Exception, obj.delete)
        self.assertEqual(Organisation.objects.count(), 1)
