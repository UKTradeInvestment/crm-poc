from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy

from .models import Organisation


class OrganisationMixin(object):
    model = Organisation
    context_object_name = 'organisation'


class Index(OrganisationMixin, ListView):
    context_object_name = 'organisations'


class Create(OrganisationMixin, CreateView):
    fields = [
        'name', 'alias',
        'uk_organisation', 'country',
        'postcode', 'address1', 'uk_region',
        'country_code', 'area_code', 'phone_number',
        'email_address', 'sector'
    ]


class Update(OrganisationMixin, UpdateView):
    fields = [
        'name', 'alias',
        'uk_organisation', 'country',
        'postcode', 'address1', 'uk_region',
        'country_code', 'area_code', 'phone_number',
        'email_address', 'sector'
    ]


class Delete(OrganisationMixin, DeleteView):
    success_url = reverse_lazy('organisation:list')
