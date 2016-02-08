from django.db import models
from django.db.models.query_utils import Q

from .query import CDMSQuery, CDMSModelIterable


class CDMSQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(CDMSQuerySet, self).__init__(model=model, query=query, using=using, hints=hints)
        self.cdms_skip = False

        self.cdms_query = CDMSQuery(model)
        self._iterable_class = CDMSModelIterable

    def _clone(self, **kwargs):
        clone = super(CDMSQuerySet, self)._clone(**kwargs)
        clone.cdms_query = self.cdms_query  # we might need to clone this
        clone.cdms_skip = self.cdms_skip
        return clone

    def get(self, *args, **kwargs):
        if not len(kwargs.keys()) == 1 or list(kwargs)[0] not in ('id', 'pk'):
            raise NotImplementedError(
                'Only getting by pk and id currently supported'
            )

        self.cdms_skip = True
        obj = super(CDMSQuerySet, self).get(*args, **kwargs)
        obj.sync_from_cdms()
        return obj

    def _filter_or_exclude(self, negate, *args, **kwargs):
        cdms_skip = self.cdms_skip or (len(kwargs.keys()) == 1 and list(kwargs)[0] in ('id', 'pk'))

        if not cdms_skip:
            if args or kwargs:
                assert self.query.can_filter(), \
                    "Cannot filter a query once a slice has been taken."

            if self.query.has_filters():
                raise NotImplementedError(
                    'Filter chaining not implemented yet, please combine your filters into one'
                )

            clone = self._clone()

            q = Q(*args, **kwargs)
            if negate:
                clone.query.add_q(~q)
                clone.cdms_query.add_q(~q)
            else:
                clone.query.add_q(q)
                clone.cdms_query.add_q(q)
        return super(CDMSQuerySet, self)._filter_or_exclude(negate, *args, **kwargs)

    # def test(self):
    #     results = cdms_conn.list('detica_omisorder', top=1, filters=[
    #         "CreatedOn ge datetime'2015-01-01T00:00:00'",
    #         "(statuscode/Value eq 790740030 or statuscode/Value eq 790740013)",
    #         "detica_servicetype/Value eq 790740000"
    #     ])
    #     aa = results['results'][0]
    #     import pdb; pdb.set_trace()
