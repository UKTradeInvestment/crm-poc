import datetime
from numbers import Number

from django.db import models
from django.db.models.sql.query import get_field_names_from_opts
from django.db.models.constants import LOOKUP_SEP
from django.utils.tree import Node
from django.core.exceptions import FieldDoesNotExist, FieldError

from cdms_api import api as cdms_conn


class CDMSCompiler(object):
    def __init__(self, query):
        self.query = query

    def get_service(self):
        return self.query.model.cdms_migrator.service

    def execute(self):
        raise NotImplementedError()


class CDMSSelectCompiler(CDMSCompiler):
    EXPRS = {
        'exact': '{field} eq {value}',
        'lt': '{field} lt {value}',
        'lte': '{field} le {value}',
        'gt': '{field} gt {value}',
        'gte': '{field} ge {value}',
    }

    def convert_value(self, value):
        if isinstance(value, Number):
            return value
        if isinstance(value, datetime.datetime):
            # TODO e.g. "CreatedOn ge datetime'2015-01-01T00:00:00'"
            raise NotImplementedError('TODO: format datetimes, should be easy')
        if isinstance(value, datetime.date):
            raise NotImplementedError('TODO: format date, should be easy')
        if isinstance(value, datetime.time):
            raise NotImplementedError('TODO: format time, should be easy')
        return "'{value}'".format(value=value)

    def execute(self):
        cdms_filters = []
        for field, expr, value in self.query.filters:
            cdms_expr = self.EXPRS.get(expr)
            if not cdms_expr:
                raise NotImplementedError('Expression %s not recognised yet' % expr)

            cdms_filters.append(
                cdms_expr.format(field=field, value=self.convert_value(value))
            )
        return cdms_conn.list(self.get_service(), filters=cdms_filters)


class CDMSInsertCompiler(CDMSCompiler):
    def execute(self):
        results = cdms_conn.create(
            self.get_service(), data=self.query.cdms_data
        )
        return results['{service}Id'.format(service=self.get_service())]


class CDMSGetCompiler(CDMSCompiler):
    def execute(self):
        return cdms_conn.get(
            self.get_service(),
            guid=self.query.cdms_pk
        )


class CDMSUpdateCompiler(CDMSCompiler):
    def execute(self):
        return cdms_conn.update(
            self.get_service(),
            guid=self.query.cdms_pk,
            data=self.query.cdms_data
        )


class CDMSRefreshCompiler(CDMSGetCompiler):
    def execute(self):
        # get cdms_obj
        cdms_data = super(CDMSRefreshCompiler, self).execute()

        migrator = self.query.model.cdms_migrator
        obj = self.query.local_obj

        # check if local obj has to be updated
        changed, modified_on = migrator.has_cdms_obj_changed(obj, cdms_data)
        if changed:
            # 1st save for the fields
            migrator.update_local_from_cdms_data(obj, cdms_data)
            obj.save(cdms_skip=True)

            # 2nd save for the modified field (this can be improved)
            obj.modified = modified_on
            obj.__class__.objects.filter(pk=obj.pk).update(modified=modified_on)

        return obj


class CDMSModelIterable(models.query.ModelIterable):
    def __iter__(self):
        if not self.queryset.cdms_skip:
            cdms_query = self.queryset.cdms_query
            # results = CDMSSelectCompiler(cdms_query).execute()

        return super(CDMSModelIterable, self).__iter__()


class CDMSQuery(object):
    compiler = CDMSCompiler

    def __init__(self, model):
        self.model = model

        self.filters = []

    def add_q(self, q_object):
        self._add_q(q_object)

    def _add_q(self, q_object, branch_negated=False, current_negated=False):
        if q_object.connector != q_object.AND:
            raise NotImplementedError(
                'OR filtering not implemented yet, please only use AND'
            )

        connector = q_object.connector
        current_negated = current_negated ^ q_object.negated
        branch_negated = branch_negated or q_object.negated
        # target_clause = self.where_class(connector=connector,
        #                                  negated=q_object.negated)
        for child in q_object.children:
            if isinstance(child, Node):
                child_clause, needed_inner = self._add_q(
                    child, branch_negated,
                    current_negated
                )
            else:
                field_name, lookup, value = self.build_filter(
                    child, branch_negated=branch_negated,
                    connector=connector,
                    current_negated=current_negated
                )
                self.filters.append(
                    (field_name, lookup, value)
                )
            # if child_clause:
            #     target_clause.add(child_clause, connector)

    def solve_lookup_type(self, lookup):
        """
        Solve the lookup type from the lookup (eg: 'foobar__id__icontains')
        """
        lookup_splitted = lookup.split(LOOKUP_SEP)
        _, field, _, lookup_parts = self.names_to_path(lookup_splitted, self.model._meta)

        field_parts = lookup_splitted[0:len(lookup_splitted) - len(lookup_parts)]
        if len(lookup_parts) == 0:
            lookup_parts = ['exact']
        elif len(lookup_parts) > 1:
            if not field_parts:
                raise FieldError(
                    'Invalid lookup "%s" for model %s".' %
                    (lookup, self.model.__name__))
        return lookup_parts, field_parts, False

    def names_to_path(self, names, opts, fail_on_missing=False):
        path = []
        # names_with_path = []
        for pos, name in enumerate(names):
            # cur_names_with_path = (name, [])
            if name == 'pk':
                name = opts.pk.name

            field = None
            try:
                field = opts.get_field(name)
            except FieldDoesNotExist:
                pass

            if field is not None:
                if field.is_relation:
                    raise NotImplementedError(
                        'Only direct access to fields implemented at the moment'
                    )
                """
                # Fields that contain one-to-many relations with a generic
                # model (like a GenericForeignKey) cannot generate reverse
                # relations and therefore cannot be used for reverse querying.
                if field.is_relation and not field.related_model:
                    raise FieldError(
                        "Field %r does not generate an automatic reverse "
                        "relation and therefore cannot be used for reverse "
                        "querying. If it is a GenericForeignKey, consider "
                        "adding a GenericRelation." % name
                    )
                """
                try:
                    model = field.model._meta.concrete_model
                except AttributeError:
                    model = None
            else:
                # We didn't find the current field, so move position back
                # one step.
                pos -= 1
                if pos == -1 or fail_on_missing:
                    field_names = list(get_field_names_from_opts(opts))
                    available = sorted(field_names)
                    raise FieldError("Cannot resolve keyword %r into field. "
                                     "Choices are: %s" % (name, ", ".join(available)))
                break

            # Check if we need any joins for concrete inheritance cases (the
            # field lives in parent, but we are currently in one of its
            # children)
            if model is not opts.model:
                raise NotImplementedError(
                    'Only direct access to fields implemented at the moment'
                )
                """
                # The field lives on a base class of the current model.
                # Skip the chain of proxy to the concrete proxied model
                proxied_model = opts.concrete_model

                for int_model in opts.get_base_chain(model):
                    if int_model is proxied_model:
                        opts = int_model._meta
                    else:
                        final_field = opts.parents[int_model]
                        targets = (final_field.remote_field.get_related_field(),)
                        opts = int_model._meta
                        path.append(PathInfo(final_field.model._meta, opts, targets, final_field, False, True))
                        cur_names_with_path[1].append(
                            PathInfo(final_field.model._meta, opts, targets, final_field, False, True)
                        )
                """

            if hasattr(field, 'get_path_info'):
                raise NotImplementedError(
                    'Only direct access to fields implemented at the moment'
                )
                """
                pathinfos = field.get_path_info()
                if not allow_many:
                    for inner_pos, p in enumerate(pathinfos):
                        if p.m2m:
                            cur_names_with_path[1].extend(pathinfos[0:inner_pos + 1])
                            names_with_path.append(cur_names_with_path)
                            raise MultiJoin(pos + 1, names_with_path)
                last = pathinfos[-1]
                path.extend(pathinfos)
                final_field = last.join_field
                opts = last.to_opts
                targets = last.target_fields
                cur_names_with_path[1].extend(pathinfos)
                names_with_path.append(cur_names_with_path)
                """
            else:
                # Local non-relational field.
                final_field = field
                targets = (field,)
                if fail_on_missing and pos + 1 != len(names):
                    raise FieldError(
                        "Cannot resolve keyword %r into field. Join on '%s'"
                        " not permitted." % (names[pos + 1], name))
                break
        return path, final_field, targets, names[pos + 1:]

    def build_filter(self, filter_expr, branch_negated=False, current_negated=False, connector=None):
        arg, value = filter_expr
        lookups, parts, reffed_expression = self.solve_lookup_type(arg)

        value, lookups = self.prepare_lookup_value(value, lookups)

        if len(lookups) != 1:
            raise NotImplementedError('Only one lookup implemented at the moment')

        if reffed_expression:
            raise NotImplementedError('Reffed expressions not implemented yet')

        _, field, targets, _ = self.names_to_path(
            parts, self.model._meta, fail_on_missing=True
        )

        field_name = field.name
        cdms_field_name, _, _ = self.model.cdms_migrator.get_fields_mapping(field_name)

        return cdms_field_name, lookups[0], value

    def prepare_lookup_value(self, value, lookups):
        # Default lookup if none given is exact.
        if len(lookups) == 0:
            lookups = ['exact']
        # Interpret '__exact=None' as the sql 'is NULL'; otherwise, reject all
        # uses of None as a query value.
        if value is None:
            raise NotImplementedError('Cannot use None as value, not implemented yet')
            """
            if lookups[-1] not in ('exact', 'iexact'):
                raise ValueError("Cannot use None as a query value")
            lookups[-1] = 'isnull'
            value = True
            """
        elif hasattr(value, 'resolve_expression'):
            raise NotImplementedError('Can only use raw values, anything else has not been implemented yet')
            """
            pre_joins = self.alias_refcount.copy()
            value = value.resolve_expression(self, reuse=can_reuse, allow_joins=allow_joins)
            used_joins = [k for k, v in self.alias_refcount.items() if v > pre_joins.get(k, 0)]
            """
        # Subqueries need to use a different set of aliases than the
        # outer query. Call bump_prefix to change aliases of the inner
        # query (the value).
        if hasattr(value, 'query') and hasattr(value.query, 'bump_prefix'):
            raise NotImplementedError('Can only use raw values, anything else has not been implemented yet')
            """
            value = value._clone()
            value.query.bump_prefix(self)
            """
        if hasattr(value, 'bump_prefix'):
            raise NotImplementedError('Can only use raw values, anything else has not been implemented yet')
            """
            value = value.clone()
            value.bump_prefix(self)
            """

        return value, lookups

    def get_compiler(self):
        return self.compiler(query=self)


class GetQuery(CDMSQuery):
    compiler = CDMSGetCompiler

    def __init__(self, *args, **kwargs):
        super(GetQuery, self).__init__(*args, **kwargs)
        self.cdms_pk = None

    def set_cdms_pk(self, cdms_pk):
        self.cdms_pk = cdms_pk


class InsertQuery(CDMSQuery):
    compiler = CDMSInsertCompiler

    def __init__(self, *args, **kwargs):
        super(InsertQuery, self).__init__(*args, **kwargs)
        self.cdms_data = {}

    def insert_value(self, obj):
        self.cdms_data = self.model.cdms_migrator.update_cdms_data_from_local(obj, {})


class UpdateQuery(CDMSQuery):
    compiler = CDMSUpdateCompiler

    def __init__(self, *args, **kwargs):
        super(UpdateQuery, self).__init__(*args, **kwargs)
        self.cdms_pk = None
        self.cdms_data = {}

    def get_cdms_obj(self):
        query = GetQuery(self.model)
        query.set_cdms_pk(self.cdms_pk)
        return query.get_compiler().execute()

    def add_update_fields(self, cdms_pk, values):
        self.cdms_pk = cdms_pk
        cdms_data = self.get_cdms_obj()
        self.cdms_data = self.model.cdms_migrator.update_cdms_data_from_values(values, cdms_data)


class RefreshQuery(GetQuery):
    compiler = CDMSRefreshCompiler

    def __init__(self, *args, **kwargs):
        super(GetQuery, self).__init__(*args, **kwargs)
        self.local_obj = None

    def set_obj(self, obj):
        self.set_cdms_pk(obj.cdms_pk)
        self.local_obj = obj
