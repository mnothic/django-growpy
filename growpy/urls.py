__author__ = 'themanda'
from django.conf.urls import patterns, url
from growpy import views

urlpatterns = patterns('',
    url(r'^$', views.Index.as_view()),
    url(r'^node/list/$', views.NodeList.as_view()),
    url(r'^node/fs/list/(?P<id>\d+)$', views.GetFSByNodeJSON.as_view()),
    url(r'^getnodes/$', views.GetNodesJSON.as_view()),
    url(r'^node/add/$', views.NodeAdd.as_view()),
    url(r'^node/del/$', views.NodeDel.as_view()),
    url(r'^node/update/$', views.NodeUpdate.as_view()),
    url(r'^node/fs/range/$', views.RangeSelector.as_view()),
    url(r'^node/fs/chart/$', views.Graph.as_view()),
    url(r'^getstat/(?P<node>\d+)/(?P<fs>\d+)/(?P<year>\d{4})/(?P<fmonth>\d{2})/(?P<tmonth>\d{2})/$',
        views.ChartFileSystemStatsJSON.as_view()),
)