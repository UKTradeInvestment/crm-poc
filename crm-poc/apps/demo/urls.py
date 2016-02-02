from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^organization/$', views.organization_view, name='organization'),
]
