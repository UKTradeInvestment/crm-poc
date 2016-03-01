from django.db.models import Count

from migrator.tests.queries.models import SimpleObj
from migrator.tests.queries.base import BaseMockedCDMSApiTestCase


class SingleObjMixin(object):
    def setUp(self):
        super(SingleObjMixin, self).setUp()
        self.obj = SimpleObj.objects.mark_as_cdms_skip().create(
            cdms_pk='cdms-pk', name='name'
        )


class AnnotateTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.annotate, Count('name')
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().annotate(Count('name')))
        self.assertNoAPICalled()


class ReverseTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.reverse
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().reverse())
        self.assertNoAPICalled()


class DistinctTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.distinct
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().distinct())
        self.assertNoAPICalled()


class ValuesTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.values
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().values())
        self.assertNoAPICalled()


class ValuesListTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.values_list
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().values_list())
        self.assertNoAPICalled()


class DatesTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.dates, 'd_field', 'year'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().dates('d_field', 'year'))
        self.assertNoAPICalled()


class DatetimesTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.datetimes, 'd_field', 'year'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().datetimes('dt_field', 'year'))
        self.assertNoAPICalled()


class NoneTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        ret = list(SimpleObj.objects.none())
        self.assertEqual(ret, [])
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().none())
        self.assertNoAPICalled()


class SelectRelatedTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.select_related
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().select_related('fk_obj').get(pk=self.obj.pk)
        self.assertNoAPICalled()


class PrefetchRelatedTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.prefetch_related
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().prefetch_related('fk_obj').get(pk=self.obj.pk)
        self.assertNoAPICalled()


class ExtraTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.extra, select={'is_recent': "dt_field > '2006-01-01'"}
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().extra(select={'is_recent': "dt_field > '2006-01-01'"}))
        self.assertNoAPICalled()


class DeferTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.defer, 'name'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().defer('name'))
        self.assertNoAPICalled()


class OnlyTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.only, 'name'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().only('name'))
        self.assertNoAPICalled()


class RawTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.raw, 'select * from queries_simpleobj'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        list(SimpleObj.objects.mark_as_cdms_skip().raw('select * from queries_simpleobj'))
        self.assertNoAPICalled()


class GetOrCreateTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.get_or_create, name='name', defaults={'int_field': 1}
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().get_or_create(name='name', defaults={'int_field': 1})
        self.assertNoAPICalled()


class UpdateOrCreateTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.update_or_create, name='name', defaults={'int_field': 1}
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().update_or_create(name='name', defaults={'int_field': 1})
        self.assertNoAPICalled()


class CountTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.count
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().count()
        self.assertNoAPICalled()


class InBulkTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.in_bulk, [1, 2]
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().in_bulk([1, 2])
        self.assertNoAPICalled()


class LatestTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.latest, 'dt_field'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().latest('dt_field')
        self.assertNoAPICalled()


class EarliestTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.earliest, 'dt_field'
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().earliest('dt_field')
        self.assertNoAPICalled()


class FirstTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.first
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().first()
        self.assertNoAPICalled()


class LastTestCase(SingleObjMixin, BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.last
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().last()
        self.assertNoAPICalled()


class AggregateTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.aggregate, Count('name')
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().aggregate(Count('name'))
        self.assertNoAPICalled()


class ExistsTestCase(BaseMockedCDMSApiTestCase):
    def test(self):
        self.assertRaises(
            NotImplementedError,
            SimpleObj.objects.exists
        )
        self.assertNoAPICalled()

    def test_skip_cdms(self):
        SimpleObj.objects.mark_as_cdms_skip().exists()
        self.assertNoAPICalled()
