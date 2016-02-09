from django.db import models
from django.db.models.query_utils import Q

from .query import CDMSQuery, CDMSModelIterable, InsertQuery, UpdateQuery


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

    def _insert(self, objs, fields, return_id=False, raw=False, using=None):
        return_val = super(CDMSQuerySet, self)._insert(objs, fields, return_id=return_id, raw=raw, using=using)

        if not self.cdms_skip:
            if not return_id or len(objs) > 1:
                raise NotImplementedError(
                    'Bulk create not implemented yet'
                )

            # insert in cdms
            obj = objs[0]
            query = InsertQuery(self.model)
            query.insert_value(obj)
            cdms_pk = query.get_compiler().execute()

            # update cdms_pk local
            # TODO make sure the cdms update doesn't happen
            obj.cdms_pk = cdms_pk
            self.filter(pk=return_val).update(cdms_pk=cdms_pk)

        return return_val

    def _update(self, values):
        return_val = super(CDMSQuerySet, self)._update(values)

        if not self.cdms_skip:
            model_values = []
            cdms_pk = None
            for field, _, value in values:
                if field.name == 'cdms_pk':
                    cdms_pk = value
                else:
                    model_values.append(
                        (field, value)
                    )

            if not cdms_pk:
                raise NotImplementedError(
                    'Cannot update without cdms pk'
                )

            query = UpdateQuery(self.model)
            query.add_update_fields(cdms_pk, model_values)
            query.get_compiler().execute()

        return return_val

    # def test(self):
    #     results = cdms_conn.list('detica_omisorder', top=1, filters=[
    #         "CreatedOn ge datetime'2015-01-01T00:00:00'",
    #         "(statuscode/Value eq 790740030 or statuscode/Value eq 790740013)",
    #         "detica_servicetype/Value eq 790740000"
    #     ])
    #     aa = results['results'][0]
    #     import pdb; pdb.set_trace()


class CDMSManager(models.Manager.from_queryset(CDMSQuerySet)):
    pass
