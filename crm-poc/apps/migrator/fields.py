from django.utils.functional import cached_property
from django.db.models.fields.related import ForeignKey
from django.db.models.fields.related_descriptors import ReverseManyToOneDescriptor, \
    create_reverse_many_to_one_manager


class ReverseManyToOneDescriptor(ReverseManyToOneDescriptor):
    @cached_property
    def related_manager_cls(self):
        superclass = create_reverse_many_to_one_manager(
            self.rel.related_model._default_manager.__class__,
            self.rel,
        )

        class RelatedManager(superclass):
            def get_queryset(self):
                qs = super(RelatedManager, self).get_queryset()
                qs._cdms_known_related_objects = {self.field.name: {self.instance.cdms_pk: self.instance}}
                return qs
        return RelatedManager


class CDMSForeignKey(ForeignKey):
    related_accessor_class = ReverseManyToOneDescriptor
