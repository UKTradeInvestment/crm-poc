from unittest import skip

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase


class CreateWithSaveTestCase(BaseMockedCDMSApiTestCase):
    def test_success(self):
        """
        obj.save() should create a new obj in local and cdms if it doesn't exist.
        """
        obj = SimpleObj()
        obj.name = 'simple obj'

        self.assertEqual(obj.cdms_pk, '')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        obj.save()
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        self.assertNotEqual(obj.cdms_pk, '')

        self.assertAPICreateCalled(
            SimpleObj, kwargs={'data': {'Name': 'simple obj', 'DateTimeField': None, 'IntField': None}}
        )
        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])

    def test_exception_triggers_rollback(self):
        """
        In case of exceptions during obj.save(), no changes should be reflected in the db.
        """
        self.mocked_cdms_api.create.side_effect = Exception

        obj = SimpleObj()
        obj.name = 'simple obj'

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        self.assertRaises(Exception, obj.save)
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)

        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])


class CreateWithManagerTestCase(BaseMockedCDMSApiTestCase):
    def test_success(self):
        """
        MyObject.objects.create() should create a new obj in local and cdms.
        """
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        obj = SimpleObj.objects.create(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        self.assertNotEqual(obj.cdms_pk, '')

        self.assertAPICreateCalled(
            SimpleObj, kwargs={'data': {'Name': 'simple obj', 'DateTimeField': None, 'IntField': None}}
        )
        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])

    def test_exception_triggers_rollback(self):
        """
        In case of exceptions during MyObject.objects.create(), no changes should be reflected in the db.
        """
        self.mocked_cdms_api.create.side_effect = Exception

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        self.assertRaises(
            Exception,
            SimpleObj.objects.create, name='simple obj'
        )
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)

        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])

    @skip('TODO: to be fixed')
    def test_with_bulk_create(self):
        """
        We should support MyObject.objects.bulk_create(obj1, obj2) which should create the objects
        in local and cdms.
        """
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        SimpleObj.objects.bulk_create(
            SimpleObj(name='simple obj1'),
            SimpleObj(name='simple obj2')
        )
        self.assertAPICreateCalled(
            SimpleObj,
            data=[
                {'data': {'Name': 'simple obj1'}},
                {'data': {'Name': 'simple obj2'}}
            ],
            tot=2
        )
        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])

    @skip('TODO: to be fixed')
    def test_exception_triggers_rollback_with_bulk_create(self):
        """
        If we decide to support bulk_create, exceptions in cdms calls should rollback the changes.
        """
        self.mocked_cdms_api.create.side_effect = Exception

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        self.assertRaises(
            Exception,
            SimpleObj.objects.bulk_create, [
                SimpleObj(name='simple obj'),
                SimpleObj(name='simple obj2')
            ]
        )
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)

        self.assertAPINotCalled(['list', 'update', 'delete', 'get'])


class CreateWithExtraManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be decided')
    def test_success(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_exception_triggers_rollback(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_exception_triggers_rollback_with_bulk_create(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass


class CreateWithSaveSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_success(self):
        """
        When calling obj.save(cdms_skip=True), changes should only happen in local, not in cdms.
        """
        obj = SimpleObj()
        obj.name = 'simple obj'

        self.assertEqual(obj.cdms_pk, '')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        obj.save(cdms_skip=True)
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        self.assertEqual(obj.cdms_pk, '')

        self.assertNoAPICalled()


class CreateWithManagerSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_with_create(self):
        """
        When calling MyObject.objects.skip_cdms().create(), changes should only happen in local, not in cdms.
        """
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        obj = SimpleObj.objects.skip_cdms().create(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        self.assertEqual(obj.cdms_pk, '')

        self.assertNoAPICalled()

    @skip('TODO: to be fixed')
    def test_with_bulk_create(self):
        """
        We should support MyObject.objects.skip_cdms().bulk_create(obj1, obj2) which should create the objects
        in local only.
        """
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)
        SimpleObj.objects.skip_cdms().bulk_create(
            SimpleObj(name='simple obj1'),
            SimpleObj(name='simple obj2')
        )

        self.assertNoAPICalled()
