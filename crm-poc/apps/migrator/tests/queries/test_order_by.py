from unittest import skip

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase


class OrderByTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be fixed')
    def test_order_by_one_field(self):
        pass

    @skip('TODO: to be fixed')
    def test_order_by_two_fields(self):
        pass

    @skip('TODO: to be fixed')
    def test_order_by_related_obj_field(self):
        pass


class OrderBySkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_order_by_one_field(self):
        list(SimpleObj.objects.skip_cdms().order_by('name'))
        self.assertNoAPICalled()

    def test_order_by_two_fields(self):
        list(SimpleObj.objects.skip_cdms().order_by('name', 'int_field'))
        self.assertNoAPICalled()

    @skip('TODO: to be fixed')
    def test_order_by_related_obj_field(self):
        pass


class OrderByExtraManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be decided')
    def test_order_by_one_field(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_order_by_two_fields(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_order_by_related_obj_field(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass
