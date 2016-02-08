from unittest import mock
from django.test.testcases import SimpleTestCase

from cdms_api.utils import mocked_cdms_get

from migrator.query import CDMSSelectCompiler

from ..models import Organisation


class BaseSelectQueryBuilderTestCase(SimpleTestCase):
    @mock.patch('migrator.query.cdms_conn')
    def __call__(self, result, mocked_api, *args, **kwargs):
        mocked_api.get.side_effect = mocked_cdms_get
        self.mocked_api = mocked_api
        super(BaseSelectQueryBuilderTestCase, self).__call__(result, *args, **kwargs)


class CDMSSelectQueryBuilderTestCase(BaseSelectQueryBuilderTestCase):
    def test_one_exact(self):
        query = Organisation.objects.filter(name='test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.mocked_api.list.assert_called_with(
            Organisation.cdms_migrator.service,
            filters=["Name eq 'test'"]
        )

    def test_one_lt(self):
        query = Organisation.objects.filter(name__lt='test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.mocked_api.list.assert_called_with(
            Organisation.cdms_migrator.service,
            filters=["Name lt 'test'"]
        )

    def test_one_lte(self):
        query = Organisation.objects.filter(name__lte='test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.mocked_api.list.assert_called_with(
            Organisation.cdms_migrator.service,
            filters=["Name le 'test'"]
        )

    def test_one_gt(self):
        query = Organisation.objects.filter(name__gt='test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.mocked_api.list.assert_called_with(
            Organisation.cdms_migrator.service,
            filters=["Name gt 'test'"]
        )

    def test_one_gte(self):
        query = Organisation.objects.filter(name__gte='test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.mocked_api.list.assert_called_with(
            Organisation.cdms_migrator.service,
            filters=["Name ge 'test'"]
        )

    def test_two_exact(self):
        query = Organisation.objects.filter(name='test', alias='alias_test').cdms_query
        CDMSSelectCompiler(query).execute()
        self.assertEqual(self.mocked_api.list.call_count, 1)

        service = self.mocked_api.list.call_args[0][0]
        filters = self.mocked_api.list.call_args[1]['filters']
        self.assertEqual(service, Organisation.cdms_migrator.service)
        self.assertListEqual(
            sorted(filters),
            sorted([
                "Name eq 'test'",
                "optevia_Alias eq 'alias_test'"
            ])
        )


class CDMSSelectNotImplementedTestCase(BaseSelectQueryBuilderTestCase):
    def test_two_exact_chained(self):
        self.assertRaises(
            NotImplementedError,
            Organisation.objects.filter(name='test').filter, alias='alias_test'
        )
