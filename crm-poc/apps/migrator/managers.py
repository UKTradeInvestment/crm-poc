from django.db import models
from django.db.models.query_utils import Q

from .query import CDMSQuery, CDMSModelIterable, RefreshQuery, \
    InsertQuery, UpdateQuery


def only_with_cdms_skip(func):
    def wrapper(self, *args, **kwargs):
        if not self.cdms_skip:
            raise NotImplementedError(
                '{method} not implemented yet'.format(method=func.__name__)
            )

        return func(self, *args, **kwargs)
    return wrapper


class CDMSQuerySet(models.QuerySet):
    def __init__(self, model=None, query=None, using=None, hints=None):
        super(CDMSQuerySet, self).__init__(model=model, query=query, using=using, hints=hints)
        self.cdms_skip = False

        self.cdms_query = CDMSQuery(model)
        self._cdms_known_related_objects = {}  # {rel_field_name, {cdms_pk: rel_obj}}
        self._iterable_class = CDMSModelIterable

    def mark_as_cdms_skip(self):
        self.cdms_skip = True
        return self

    def _clone(self, **kwargs):
        clone = super(CDMSQuerySet, self)._clone(**kwargs)
        clone.cdms_query = self.cdms_query  # we might need to clone this
        clone.cdms_skip = self.cdms_skip

        clone._cdms_known_related_objects = self._cdms_known_related_objects
        return clone

    def none(self):
        self.cdms_query.set_empty()
        return super(CDMSQuerySet, self).none()

    def get(self, *args, **kwargs):
        original_cdms_skip = self.cdms_skip
        self.cdms_skip = True
        try:
            obj = super(CDMSQuerySet, self).get(*args, **kwargs)

            if not original_cdms_skip:
                # get cdms object
                query = RefreshQuery(self.model)
                query.set_local_obj(obj)
                obj = query.get_compiler().execute()
        finally:
            # restore old setting
            self.cdms_skip = original_cdms_skip
        return obj

    def create(self, **kwargs):
        """
        Creates a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj = self.model(**kwargs)
        self._for_write = True
        obj.save(force_insert=True, using=self.db, cdms_skip=self.cdms_skip)
        return obj

    def _filter_or_exclude(self, negate, *args, **kwargs):
        if not self.cdms_skip:
            if args or kwargs:
                assert self.query.can_filter(), \
                    "Cannot filter a query once a slice has been taken."

            if not args and not kwargs:
                if not self.query.has_filters():
                    raise NotImplementedError(
                        'Cannot yet get all objects, not implemented yet'
                    )
            else:
                if self.query.has_filters():
                    raise NotImplementedError(
                        'Filter chaining not implemented yet, please combine your filters into one'
                    )

            if not (len(kwargs.keys()) == 1 and list(kwargs)[0] in ('id', 'pk')):
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

    @only_with_cdms_skip
    def annotate(self, *args, **kwargs):
        return super(CDMSQuerySet, self).annotate(*args, **kwargs)

    @only_with_cdms_skip
    def reverse(self, *args, **kwargs):
        return super(CDMSQuerySet, self).reverse(*args, **kwargs)

    @only_with_cdms_skip
    def select_for_update(self, *args, **kwargs):
        return super(CDMSQuerySet, self).select_for_update(*args, **kwargs)

    @only_with_cdms_skip
    def distinct(self, *args, **kwargs):
        return super(CDMSQuerySet, self).distinct(*args, **kwargs)

    @only_with_cdms_skip
    def values(self, *args, **kwargs):
        return super(CDMSQuerySet, self).values(*args, **kwargs)

    @only_with_cdms_skip
    def values_list(self, *args, **kwargs):
        return super(CDMSQuerySet, self).values_list(*args, **kwargs)

    @only_with_cdms_skip
    def select_related(self, *args, **kwargs):
        return super(CDMSQuerySet, self).select_related(*args, **kwargs)

    @only_with_cdms_skip
    def prefetch_related(self, *args, **kwargs):
        return super(CDMSQuerySet, self).prefetch_related(*args, **kwargs)

    @only_with_cdms_skip
    def extra(self, *args, **kwargs):
        return super(CDMSQuerySet, self).extra(*args, **kwargs)

    @only_with_cdms_skip
    def defer(self, *args, **kwargs):
        return super(CDMSQuerySet, self).defer(*args, **kwargs)

    @only_with_cdms_skip
    def only(self, *args, **kwargs):
        return super(CDMSQuerySet, self).only(*args, **kwargs)

    @only_with_cdms_skip
    def raw(self, *args, **kwargs):
        return super(CDMSQuerySet, self).raw(*args, **kwargs)

    @only_with_cdms_skip
    def get_or_create(self, *args, **kwargs):
        return super(CDMSQuerySet, self).get_or_create(*args, **kwargs)

    @only_with_cdms_skip
    def update_or_create(self, *args, **kwargs):
        return super(CDMSQuerySet, self).update_or_create(*args, **kwargs)

    @only_with_cdms_skip
    def count(self, *args, **kwargs):
        return super(CDMSQuerySet, self).count(*args, **kwargs)

    @only_with_cdms_skip
    def in_bulk(self, *args, **kwargs):
        return super(CDMSQuerySet, self).in_bulk(*args, **kwargs)

    @only_with_cdms_skip
    def earliest(self, *args, **kwargs):
        return super(CDMSQuerySet, self).earliest(*args, **kwargs)

    @only_with_cdms_skip
    def latest(self, *args, **kwargs):
        return super(CDMSQuerySet, self).latest(*args, **kwargs)

    @only_with_cdms_skip
    def first(self, *args, **kwargs):
        return super(CDMSQuerySet, self).first(*args, **kwargs)

    @only_with_cdms_skip
    def last(self, *args, **kwargs):
        return super(CDMSQuerySet, self).last(*args, **kwargs)

    @only_with_cdms_skip
    def aggregate(self, *args, **kwargs):
        return super(CDMSQuerySet, self).aggregate(*args, **kwargs)

    @only_with_cdms_skip
    def exists(self, *args, **kwargs):
        return super(CDMSQuerySet, self).exists(*args, **kwargs)


class CDMSManager(models.Manager.from_queryset(CDMSQuerySet)):
    pass
