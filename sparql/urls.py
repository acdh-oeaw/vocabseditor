from django.conf.urls import url
from . import views

app_name = 'sparql'


urlpatterns = [
    url(r'^query/$', views.QueryView.as_view(), name='query'),
    url(r'^tunnel/$', views.query_tunnel, name='tunnel'),
]
