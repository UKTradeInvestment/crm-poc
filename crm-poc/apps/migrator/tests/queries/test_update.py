from django.db import transaction
from django.utils import timezone

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase

from cdms_api.utils import mocked_cdms_get


class UpdateWithSaveTestCase(BaseMockedCDMSApiTestCase):
    def test_save(self):
        """
        obj.save() should
            - get the related cdms obj
            - update the cdms obj
            - save local obj
        """
        # mock get call
        modified_on = timezone.now()
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        # save
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        obj.name = 'simple obj'
        obj.save()
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': 'cdms-pk'}
        )

        # check cdms update called
        expected_data = mocked_cdms_get(modified_on=modified_on)(None, None)
        expected_data.update({'Name': 'simple obj', 'DateTimeField': None, 'IntField': None})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs={
                'guid': 'cdms-pk',
                'data': expected_data
            }
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

    def test_exception_triggers_rollback(self):
        """
        In case of exceptions during cdms calls, no changes should be reflected in the db.
        """
        # mock update call
        self.mocked_cdms_api.update.side_effect = Exception

        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        # save
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        obj.name = 'new name'
        self.assertRaises(Exception, obj.save)
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': 'cdms-pk'}
        )
        self.assertAPINotCalled(['create', 'list', 'delete'])

        # check that the obj in the db didn't change
        obj = SimpleObj.objects.skip_cdms().get(pk=obj.pk)
        self.assertEqual(obj.name, 'old name')

    def test_save_with_skip_cdms(self):
        """
        obj.save(skip_cdms=True) should only update the obj in local.
        """
        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        obj.name = 'simple obj'
        obj.save(skip_cdms=True)
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        self.assertNoAPICalled()

        # check that the obj in the db changed
        obj = SimpleObj.objects.skip_cdms().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')


class UpdateWithManagerTestCase(BaseMockedCDMSApiTestCase):
    def test_update(self):
        """
        MyObject.objects.filter(...).update(...) not currently implemented
        """
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name')

        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.filter(name__icontains='name').update,
            name='new name'
        )
        self.assertNoAPICalled()

    def test_update_with_skip_cdms(self):
        """
        MyObject.objects.skip_cdms().filter(...).update(...) should only update local objs.
        """
        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        SimpleObj.objects.skip_cdms().filter(pk=obj.pk).update(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        self.assertNoAPICalled()

        # check that the obj in the db changed
        obj = SimpleObj.objects.skip_cdms().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')


class SelectForUpdateCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_select_for_update(self):
        """
        MyObject.objects.select_for_update() not currently implemented.
        """
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.select_for_update
        )

    def test_select_for_update_with_skip_cdms(self):
        """
        MyObject.objects.skip_cdms().select_for_update() should only work on local objs.
        """
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name')

        with transaction.atomic():
            entries = SimpleObj.objects.skip_cdms().select_for_update().filter(name__icontains='name')
            self.assertEqual(len(entries), 1)

            self.assertNoAPICalled()
