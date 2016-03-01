import datetime
from unittest import skip

from django.utils import timezone
from django.conf import settings

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase
from migrator.exceptions import ObjectsNotInSyncException

from cdms_api.utils import mocked_cdms_get


class BaseGetTestCase(BaseMockedCDMSApiTestCase):
    def setUp(self):
        super(BaseGetTestCase, self).setUp()
        self.obj = SimpleObj.objects.skip_cdms().create(
            cdms_pk='cdms-pk', name='name'
        )


class GetTestCase(BaseGetTestCase):
    def test_get_by_id(self):
        """
        MyObject.objects.get(pk=..) should hit the cdms api and
        return the local obj.
        """
        obj = SimpleObj.objects.get(pk=self.obj.pk)
        self.assertEqual(obj.pk, self.obj.pk)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

    def test_get_by_cdms_pk(self):
        """
        MyObject.objects.get(cdms_pk=..) when local obj exists,
        should hit the cdms api and return the local obj.
        """
        obj = SimpleObj.objects.get(cdms_pk=self.obj.cdms_pk)
        self.assertEqual(obj.pk, self.obj.pk)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

    @skip('TODO: to be fixed')
    def test_get_by_cdms_pk_when_local_obj_doesnt_exist(self):
        """
        MyObject.objects.get(cdms_pk=..) when local obj does not exist,
        should hit the cdms api, create a local obj and return it.
        """
        SimpleObj.objects.skip_cdms().all().delete()
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 0)

        cdms_pk = 'cdms-pk'

        obj = SimpleObj.objects.get(cdms_pk=cdms_pk)
        self.assertEqual(SimpleObj.objects.skip_cdms().count(), 1)
        self.assertEqual(obj.cdms_pk, cdms_pk)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': cdms_pk}
        )

    def test_get_by_other_field(self):
        """
        MyObject.objects.get(other_field=..) should work as with pk or id.
        """
        obj = SimpleObj.objects.get(name='name')
        self.assertEqual(obj.pk, self.obj.pk)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

    def test_get_with_objs_in_sync(self):
        """
        If the cdms obj and local obj are in sync:
            - get obj from local db
            - get cdms_obj from cdms
            - no local changes happen
        """
        modified_on = self.obj.modified + datetime.timedelta(
            seconds=settings.CDMS_SYNC_DELTA
        )
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        obj = SimpleObj.objects.get(pk=self.obj.pk)
        self.assertEqual(obj.modified, self.obj.modified)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

        self.assertAPINotCalled(['list', 'update', 'delete', 'create'])

    @skip('TO be decided: should we find a strategy for this case as well?')
    def test_get_with_local_more_up_to_date(self):
        """
        If the local obj is more up to date, it means that the last syncronisation didn't
        work as it should have so we raise ObjectsNotInSyncException.
        """
        modified_on = self.obj.modified - datetime.timedelta(
            seconds=settings.CDMS_SYNC_DELTA + 0.001
        )

        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(modified_on=modified_on)

        self.assertRaises(
            ObjectsNotInSyncException, SimpleObj.objects.get, pk=self.obj.pk
        )

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

        self.assertAPINotCalled(['list', 'update', 'delete', 'create'])

    def test_with_get_cdms_more_up_to_date(self):
        """
        If the cdms obj is more recent than the local one:
            - get obj from local db
            - get cdms_obj from cdms
            - update obj based on cdms_obj
        """
        modified_on = (timezone.now() + datetime.timedelta(days=1)).replace(microsecond=0)
        self.mocked_cdms_api.get.side_effect = mocked_cdms_get(
            modified_on=modified_on, get_data={
                'Name': 'new name',
                'DateTimeField': None,
                'IntField': None
            }
        )

        obj = SimpleObj.objects.get(pk=self.obj.pk)
        self.assertEqual(obj.name, 'new name')
        self.assertEqual(obj.modified, modified_on)
        self.assertEqual(obj.created, self.obj.created)

        self.assertAPIGetCalled(
            SimpleObj, kwargs={'guid': self.obj.cdms_pk}
        )

        self.assertAPINotCalled(['list', 'update', 'delete', 'create'])

    @skip('TODO to be fixed')
    def test_get_without_cdms_pk(self):
        """
        If for some reasons cdms_pk is blank, the cdms api call shouldn't happen.
        """
        self.obj.cdms_pk = ''
        self.obj.save(skip_cdms=True)

        SimpleObj.objects.get(pk=self.obj.pk)

        self.assertNoAPICalled()

    @skip('TO be decided: should be fail silently instead?')
    def test_cdms_exception_triggers_exception(self):
        """
        If an exception happens when accessing cdms, the exception is propagated.
        TODO should be catch and fail silently instead?
        """
        self.mocked_cdms_api.get.side_effect = Exception

        self.assertRaises(
            Exception, SimpleObj.objects.get, pk=self.obj.pk
        )


class GetSkipCDMSTestCase(BaseGetTestCase):
    def test_get_by_any_fields_allowed(self):
        SimpleObj.objects.skip_cdms().get(pk=self.obj.pk)
        self.assertNoAPICalled()

        SimpleObj.objects.skip_cdms().get(cdms_pk=self.obj.cdms_pk)
        self.assertNoAPICalled()


class GetWithExtraManagerTestCase(BaseGetTestCase):
    @skip('TODO to be decided')
    def test_get(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
        pass

    @skip('TODO: to be decided')
    def test_exception_triggers_rollback(self):
        """
        The output when using an extra manager at the moment is unexpected and should not be used.
        """
