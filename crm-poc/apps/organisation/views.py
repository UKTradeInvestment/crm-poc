from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.shortcuts import render

from .models import Organisation


class Index(TemplateView):
    template_name = 'organisation/index.html'


class Create(CreateView):
    model = Organisation
    fields = [
        'name', 'alias',
        'uk_organisation', 'country',
        'postcode', 'address1', 'uk_region',
        'country_code', 'area_code', 'phone_number',
        'email_address', 'sector'
    ]
    context_object_name = 'organisation'


class Update(UpdateView):
    model = Organisation
    fields = [
        'name', 'alias', 'email_address'
    ]
    context_object_name = 'organisation'
