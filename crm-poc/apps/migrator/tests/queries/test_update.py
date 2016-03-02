import datetime
from unittest import skip

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


class UpdateWithManagerTestCase(BaseMockedCDMSApiTestCase):
    def test_update_outofdate_single_obj(self):
        """
        MyObject.objects.filter(pk=...).update(...):
            - gets the local obj
            - gets the cdms obj
            - updates local obj as cdms one more up to date
            - updates the values in 'update' on local obj
            - updates the values in 'updates' on cdms obj
        """
        # mock get call
        get_mocked_data = mocked_cdms_get(
            modified_on=timezone.now() + datetime.timedelta(hours=1),
            get_data={
                'Name': 'name',
                'DateTimeField': None,
                'IntField': 20
            }
        )
        self.mocked_cdms_api.get.side_effect = get_mocked_data

        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name', int_field=10)

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        SimpleObj.objects.filter(pk=obj.pk).update(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs=[
                {'guid': 'cdms-pk'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk'}   # cdms get before updating it
            ], tot=2
        )

        # check cdms update called
        expected_data = get_mocked_data(None, None)
        expected_data.update({'Name': 'simple obj'})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs={
                'guid': 'cdms-pk',
                'data': expected_data
            }
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

        # reload local obj and check if update happened
        # also check that other fields got updated as well as cdms obj had a more recent version of them
        obj = SimpleObj.objects.skip_cdms().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')
        self.assertEqual(obj.int_field, 20)

    def test_update_uptodate_single_obj(self):
        """
        MyObject.objects.filter(pk=...).update(...):
            - gets the local obj
            - gets the cdms obj
            - updates the values in 'update' on local obj
            - updates the values in 'updates' on cdms obj
        """
        # mock get call
        get_mocked_data = mocked_cdms_get(
            modified_on=timezone.now(),
            get_data={
                'Name': 'name',
                'DateTimeField': None,
                'IntField': 20
            }
        )
        self.mocked_cdms_api.get.side_effect = get_mocked_data

        # create without cdms and then save
        obj = SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name', int_field=10)

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        SimpleObj.objects.filter(pk=obj.pk).update(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs=[
                {'guid': 'cdms-pk'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk'}   # cdms get before updating it
            ], tot=2
        )

        # check cdms update called
        expected_data = get_mocked_data(None, None)
        expected_data.update({'Name': 'simple obj'})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs={
                'guid': 'cdms-pk',
                'data': expected_data
            }
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

        # reload local obj and check if update happened
        # also check that other fields didn't get updated as local obj had a more recent version of them
        obj = SimpleObj.objects.skip_cdms().get(pk=obj.pk)
        self.assertEqual(obj.name, 'simple obj')
        self.assertEqual(obj.int_field, 10)  # 10 not 20

    def test_update_multiple_objs(self):
        """
        MyObject.objects.filter(name__icontains='asdfas').update(...):
            - gets the local objs
            - gets the cdms objs
            - updates some local obj as cdms one more up to date
            - updates the values in 'update' on local obj
            - updates the values in 'updates' on cdms obj

        In this instance:
            - cdms-pk1 local obj is up-to date so:
                - name will change (value == 'simple obj')
                - int_field will not change (value == 10)
            - cdms-pk2 local obj is out-of-date so:
                - name will change (value == 'simple obj')
                - int_field will change (value == 20)
        """
        # mock get call
        get_mocked_data = {
            'cdms-pk1': mocked_cdms_get(
                modified_on=timezone.now(),
                get_data={
                    'Name': 'old name 1',
                    'DateTimeField': None,
                    'IntField': 20
                }
            ),
            'cdms-pk2': mocked_cdms_get(
                modified_on=timezone.now() + datetime.timedelta(hours=1),
                get_data={
                    'Name': 'old name 2',
                    'DateTimeField': None,
                    'IntField': 20
                }
            ),
        }

        def get_mocked_func(service, guid):
            return get_mocked_data[guid](service, guid)

        self.mocked_cdms_api.get.side_effect = get_mocked_func

        # create without cdms and then save
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk1', name='old name 1', int_field=10)
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk2', name='old name 2', int_field=10)

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)
        SimpleObj.objects.filter(name__icontains='name').update(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs=[
                {'guid': 'cdms-pk1'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk2'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk1'},  # cdms get before updating it
                {'guid': 'cdms-pk2'}   # cdms get before updating it
            ],
            tot=4
        )

        # check cdms update called
        expected_data_1 = get_mocked_data['cdms-pk1'](None, None)
        expected_data_1.update({'Name': 'simple obj'})

        expected_data_2 = get_mocked_data['cdms-pk2'](None, None)
        expected_data_2.update({'Name': 'simple obj'})
        self.assertAPIUpdateCalled(
            SimpleObj,
            kwargs=[
                {
                    'guid': 'cdms-pk1',
                    'data': expected_data_1
                },
                {
                    'guid': 'cdms-pk2',
                    'data': expected_data_2
                }
            ],
            tot=2
        )
        self.assertAPINotCalled(['list', 'create', 'delete'])

        # reload local objs and check that updates happened
        # also check that local obj_2 int_field got updated from cdms data before the current update
        obj_1 = SimpleObj.objects.skip_cdms().get(cdms_pk='cdms-pk1')
        self.assertEqual(obj_1.name, 'simple obj')
        self.assertEqual(obj_1.int_field, 10)

        obj_2 = SimpleObj.objects.skip_cdms().get(cdms_pk='cdms-pk2')
        self.assertEqual(obj_2.name, 'simple obj')
        self.assertEqual(obj_2.int_field, 20)

    def test_exception_triggers_rollback(self):
        """
        Tests that if the cdms update call fails, local changes are rolled back.

        In this instance:
            - call to update cmds-pk1 does not fail
            - call to update cdms-pk2 raises an exception

        As result, both objects get reverted back.

        IMPORTANT NOTE: the first cdms update call happened and cannot be undo so this case
            cannot be covered propertly.
            This, therefore as unexpected results.
        """
        def update_mocked_func(service, guid, data):
            if guid == 'cdms-pk1':
                from unittest import mock
                return mock.MagicMock()
            raise Exception()
        self.mocked_cdms_api.update.side_effect = update_mocked_func

        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk1', name='old name')
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk2', name='old name')

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)
        self.assertRaises(
            Exception,
            SimpleObj.objects.filter(name__icontains='name').update,
            name='simple obj'
        )
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)

        # check cdms get called
        self.assertAPIGetCalled(
            SimpleObj, kwargs=[
                {'guid': 'cdms-pk1'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk2'},  # cdms get in order to check if local obj is up-to-date
                {'guid': 'cdms-pk1'},   # cdms get before updating it
                {'guid': 'cdms-pk2'}   # cdms get before updating it
            ], tot=4
        )

        self.assertAPINotCalled(['create', 'list', 'delete'])

        # check that the obj in the db didn't change
        obj_1 = SimpleObj.objects.skip_cdms().get(cdms_pk='cdms-pk1')
        self.assertEqual(obj_1.name, 'old name')

        obj_2 = SimpleObj.objects.skip_cdms().get(cdms_pk='cdms-pk2')
        self.assertEqual(obj_2.name, 'old name')


class UpdateWithSaveSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_save(self):
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


class UpdateWithManagerSkipCDMSTestCase(BaseMockedCDMSApiTestCase):
    def test_update_single_obj(self):
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

    def test_update_multiple_objs(self):
        # create without cdms and then save
        obj1 = SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name')
        obj2 = SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk2', name='old name 2')

        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)
        SimpleObj.objects.skip_cdms().filter(name__icontains='name').update(name='simple obj')
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 2)

        self.assertNoAPICalled()

        # check that the objs in the db changed
        obj1 = SimpleObj.objects.skip_cdms().get(pk=obj1.pk)
        self.assertEqual(obj1.name, 'simple obj')
        obj2 = SimpleObj.objects.skip_cdms().get(pk=obj2.pk)
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
        MyObject.objects.skip_cdms().select_for_update() working as usual.
        """
        SimpleObj.objects.skip_cdms().create(cdms_pk='cdms-pk', name='old name')

        with transaction.atomic():
            entries = SimpleObj.objects.skip_cdms().select_for_update().filter(name__icontains='name')
            self.assertEqual(len(entries), 1)

            self.assertNoAPICalled()
