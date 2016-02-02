from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.Index.as_view(), name='index'),
    url(r'^create/$', views.Create.as_view(), name='create'),
    url(r'^(?P<pk>[0-9]+)/$', views.Update.as_view(), name='update'),
]
