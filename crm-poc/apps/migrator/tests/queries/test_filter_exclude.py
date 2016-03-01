from unittest import skip

from django.db.models import Q

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase


class FilterTestCase(BaseMockedCDMSApiTestCase):
    def test_one_field(self):
        list(SimpleObj.objects.filter(name='something'))

        self.assertAPIListCalled(
            SimpleObj, kwargs={'filters': ["Name eq 'something'"]}
        )
        self.assertAPINotCalled(['create', 'update', 'delete', 'get'])

    def test_two_fields(self):
        list(SimpleObj.objects.filter(name='something', int_field=1))

        self.assertAPIListCalled(
            SimpleObj, kwargs={'filters': ["Name eq 'something'", "IntField eq 1"]}
        )
        self.assertAPINotCalled(['create', 'update', 'delete', 'get'])

    @skip('TODO: to be fixed')
    def test_two_fields_in_chain(self):
        list(SimpleObj.objects.filter(name='something').filter(int_field=1))

        self.assertAPIListCalled(
            SimpleObj, kwargs={'filters': ["Name eq 'something'", "IntField eq 1"]}
        )
        self.assertAPINotCalled(['create', 'update', 'delete', 'get'])

    @skip('TODO: to be fixed')
    def test_two_fields_in_or(self):
        list(SimpleObj.objects.filter(Q(name='something') | Q(int_field=1)))

        self.assertAPINotCalled(['create', 'update', 'delete', 'get'])


class FilterSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_filter(self):
        list(SimpleObj.objects.skip_cdms().filter(name='something'))
        self.assertNoAPICalled()


class FilterWithExtraManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO to be decided')
    def test_filter(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass


class ExcludeTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be fixed')
    def test_one_field(self):
        list(SimpleObj.objects.exclude(name='something'))

    @skip('TODO: to be fixed')
    def test_two_fields(self):
        list(SimpleObj.objects.exclude(name='something', int_field=1))

    @skip('TODO: to be fixed')
    def test_two_fields_in_chain(self):
        list(SimpleObj.objects.exclude(name='something').exclude(int_field=1))

    @skip('TODO: to be fixed')
    def test_two_fields_in_or(self):
        list(SimpleObj.objects.exclude(Q(name='something') | Q(int_field=1)))

    @skip('TODO: to be fixed')
    def test_filter_exclude(self):
        list(SimpleObj.objects.filter(name='something').exclude(int_field=1))


class ExcludeSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_exclude(self):
        list(SimpleObj.objects.skip_cdms().exclude(name='something'))
        self.assertNoAPICalled()


class ExcludWithExtraManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO to be decided')
    def test_exclude(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass
