from unittest import skip

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase


class BaseDeleteTestCase(BaseMockedCDMSApiTestCase):
    def setUp(self):
        super(BaseDeleteTestCase, self).setUp()
        self.obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk', name='name'
        )


class DeleteTestCase(BaseDeleteTestCase):
    @skip('TODO: to be fixed')
    def test_delete_by_queryset(self):
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 1)
        SimpleObj.objects.filter(name='name').delete()
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 0)

        self.assertAPIDeleteCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )
        self.assertAPINotCalled(['list', 'update', 'get', 'create'])

    @skip('TODO: to be fixed')
    def test_delete_from_obj(self):
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 1)
        self.obj.delete()
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 0)

        self.assertAPIDeleteCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )
        self.assertAPINotCalled(['list', 'update', 'get', 'create'])

    @skip('TODO: to be fixed')
    def test_exception_triggers_rollback(self):
        """
        In case of exceptions with cdms calls, no changes should be reflected in the db.
        """
        pass


class DeleteSkipCDMSTestCase(BaseDeleteTestCase):
    def test_delete_by_queryset(self):
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 1)
        SimpleObj.objects.mark_as_cdms_skip().filter(name='name').delete()
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 0)

        self.assertNoAPICalled()

    def test_delete_from_obj(self):
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 1)
        self.obj.delete()
        self.assertEqual(SimpleObj.objects.mark_as_cdms_skip().count(), 0)

        self.assertNoAPICalled()


class DeleteWithExtraManagerTestCase(BaseDeleteTestCase):
    @skip('TODO to be decided')
    def test_delete_by_queryset(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_delete_from_obj(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
