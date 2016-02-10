from unittest import mock
from django.test.testcases import TestCase

from cdms_api.utils import mocked_cdms_get

from ..models import Organisation


class BaseFilterBuilderTestCase(TestCase):
    @mock.patch('migrator.query.cdms_conn')
    def __call__(self, result, mocked_api, *args, **kwargs):
        mocked_api.get.side_effect = mocked_cdms_get
        self.mocked_api = mocked_api
        super(BaseFilterBuilderTestCase, self).__call__(result, *args, **kwargs)


class FilterBuilderTestCase(BaseFilterBuilderTestCase):
    def assert_list_filters(self, filters):
        self.assertEqual(self.mocked_api.list.call_count, 1)

        service = self.mocked_api.list.call_args[0][0]
        called_filters = self.mocked_api.list.call_args[1]['filters']
        self.assertEqual(service, Organisation.cdms_migrator.service)
        self.assertListEqual(sorted(called_filters), sorted(filters))

    def test_one_exact(self):
        list(Organisation.objects.filter(name='test'))
        self.assert_list_filters(["Name eq 'test'"])

    def test_one_lt(self):
        list(Organisation.objects.filter(name__lt='test'))
        self.assert_list_filters(["Name lt 'test'"])

    def test_one_lte(self):
        list(Organisation.objects.filter(name__lte='test'))
        self.assert_list_filters(["Name le 'test'"])

    def test_one_gt(self):
        list(Organisation.objects.filter(name__gt='test'))
        self.assert_list_filters(["Name gt 'test'"])

    def test_one_gte(self):
        list(Organisation.objects.filter(name__gte='test'))
        self.assert_list_filters(["Name ge 'test'"])

    def test_two_exact(self):
        list(Organisation.objects.filter(name='test', alias='alias_test'))
        self.assert_list_filters([
            "Name eq 'test'",
            "optevia_Alias eq 'alias_test'"
        ])

    def test_contains(self):
        list(Organisation.objects.filter(name__contains='test'))
        self.assert_list_filters([
            "substringof('test', Name)"
        ])

    def test_icontains(self):
        list(Organisation.objects.filter(name__icontains='test'))
        self.assert_list_filters([
            "substringof('test', Name)"
        ])


class FiltersNotImplementedTestCase(BaseFilterBuilderTestCase):
    def test_two_exact_chained(self):
        self.assertRaises(
            NotImplementedError,
            Organisation.objects.filter(name='test').filter, alias='alias_test'
        )
