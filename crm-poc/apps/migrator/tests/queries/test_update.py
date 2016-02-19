from unittest import skip

from django.db import transaction
from django.utils import timezone

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase

from cdms_api.utils import mocked_cdms_get


class UpdateWithSaveTestCase(BaseMockedCDMSApiTestCase):
    def test_save(self):
        """
        obj.save() should update the obj in local and cdms.
        """
        # mock get call
        modified_on = timezone.now()
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        # create without cdms and then save
        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.count(), 1)
        obj.name = 'simple obj'
        obj.save()
        self.assertEqual(SimpleObj.objects.count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': 'cdms-pk'}
        )

        # check cdms update called
        expected_data = mocked_cdms_get(modified_on=modified_on)(None, None)
        expected_data.update({'Name': 'simple obj', 'DateField': None, 'IntField': None})
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
        In case of exceptions during obj.save(), no changes should be reflected in the db.
        """
        # set up
        self.mocked_cdms_api.update.side_effect = Exception

        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        # save
        self.assertEqual(SimpleObj.objects.count(), 1)
        obj.name = 'new name'
        self.assertRaises(Exception, obj.save)
        self.assertEqual(SimpleObj.objects.count(), 1)

        self.assertAPIGetCalled(SimpleObj, kwargs={'guid': 'cdms-pk'})
        self.assertAPINotCalled(['create', 'list', 'delete'])

        # check that the obj in the db didn't change
        obj = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj.pk)
        self.assertEqual(obj.name, 'old name')


class UpdateWithManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be fixed')
    def test_update_single_obj(self):
        """
        We should probably support MyObject.objects.filter(pk=...).update(...) or just raise NotImplementedError
        instead.
        """
        # mock get call
        modified_on = timezone.now()
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        # create without cdms and then save
        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.count(), 1)
        SimpleObj.objects.filter(pk=obj.pk).update(name='simple obj')
        self.assertEqual(SimpleObj.objects.count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': 'cdms-pk'}
        )

        # check cdms update called
        expected_data = mocked_cdms_get(modified_on=modified_on)(None, None)
        expected_data.update({'Name': 'simple obj'})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs={
                'guid': 'cdms-pk',
                'data': expected_data
            }
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

    @skip('TODO: to be fixed')
    def test_update_multiple_objs(self):
        """
        We should probably support MyObject.objects.filter(name__icontains='asdfas').update(...) or just raise
        NotImplementedError instead.
        """
        # mock get call
        modified_on = timezone.now()
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        # create without cdms and then save
        SimpleObj.objects.mark_as_cdms_skip().create(cdms_pk='cdms-pk', name='old name')
        SimpleObj.objects.mark_as_cdms_skip().create(cdms_pk='cdms-pk2', name='old name 2')

        self.assertEqual(SimpleObj.objects.count(), 2)
        SimpleObj.objects.filter(name__icontains='name').update(name='simple obj')
        self.assertEqual(SimpleObj.objects.count(), 2)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs=[
                {'guid': 'cdms-pk'}, {'guid': 'cdms-pk2'}
            ]
        )

        # check cdms update called
        expected_data = mocked_cdms_get(modified_on=modified_on)(None, None)
        expected_data.update({'Name': 'simple obj'})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs=[
                {
                    'guid': 'cdms-pk',
                    'data': expected_data
                },
                {
                    'guid': 'cdms-pk2',
                    'data': expected_data
                }
            ]
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

    @skip('TODO: to be fixed')
    def test_exception_triggers_rollback(self):
        """
        We should raise exception and rollback if the cdms update fails.
        """
        self.mocked_cdms_api.update.side_effect = Exception

        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.count(), 1)
        self.assertRaises(
            Exception,
            SimpleObj.objects.filter(pk=obj.pk).update,
            name='simple obj'
        )
        self.assertEqual(SimpleObj.objects.count(), 1)

        self.assertAPIGetCalled(SimpleObj, kwargs={'guid': 'cdms-pk'})
        self.assertAPINotCalled(['create', 'list', 'delete'])

        # check that the obj in the db didn't change
        obj = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj.pk)
        self.assertEqual(obj.name, 'old name')


class UpdateWithExtraManagerTestCase(BaseMockedCDMSApiTestCase):
    @skip('TODO: to be decided')
    def test_update_single_obj(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_update_multiple_objs(self):
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


class UpdateWithSaveSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_save(self):
        """
        obj.save(cdms_skip=True) should only update the obj in local.
        """
        # create without cdms and then save
        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.count(), 1)
        obj.name = 'simple obj'
        obj.save(cdms_skip=True)
        self.assertEqual(SimpleObj.objects.count(), 1)

        self.assertNoAPINotCalled()

        # check that the obj in the db changed
        obj = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')


class UpdateWithManagerSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_update_single_obj(self):
        # create without cdms and then save
        obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk',
            name='old name'
        )

        self.assertEqual(SimpleObj.objects.count(), 1)
        SimpleObj.objects.mark_as_cdms_skip().filter(pk=obj.pk).update(name='simple obj')
        self.assertEqual(SimpleObj.objects.count(), 1)

        self.assertNoAPINotCalled()

        # check that the obj in the db changed
        obj = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')

    def test_update_multiple_objs(self):
        obj1 = SimpleObj.objects.mark_as_cdms_skip().create(cdms_pk='cdms-pk', name='old name')
        obj2 = SimpleObj.objects.mark_as_cdms_skip().create(cdms_pk='cdms-pk2', name='old name 2')

        self.assertEqual(SimpleObj.objects.count(), 2)
        SimpleObj.objects.mark_as_cdms_skip().filter(name__icontains='name').update(name='simple obj')
        self.assertEqual(SimpleObj.objects.count(), 2)

        self.assertNoAPINotCalled()

        # check that the objs in the db changed
        obj1 = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj1.pk)
        self.assertEqual(obj1.name, 'simple obj')
        obj2 = SimpleObj.objects.mark_as_cdms_skip().get(pk=obj2.pk)
        self.assertEqual(obj2.name, 'simple obj')


class SelectForUpdateCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_not_implemented_without_skipping_cdms(self):
        """
        MyObject.objects.select_for_update() not supported yet.
        """
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.select_for_update
        )

    def test_as_usual_with_cdms_skip(self):
        """
        MyObject.objects.mark_as_cdms_skip().select_for_update() working as usual.
        """
        SimpleObj.objects.mark_as_cdms_skip().create(cdms_pk='cdms-pk', name='old name')

        with transaction.atomic():
            entries = SimpleObj.objects.mark_as_cdms_skip().select_for_update().filter(name__icontains='name')
            self.assertEqual(len(entries), 1)

            self.assertNoAPINotCalled()

    @skip('TODO to be decided')
    def test_as_usual_with_extra_manager(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass
