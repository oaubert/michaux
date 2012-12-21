from django.conf.urls import patterns, url, include
#from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = patterns('',
                       url(r'^$', 'base.views.root'),
                       url(r'^work/$', 'base.views.works'),
                       url(r'^work/(?P<cote>\d+)/$', 'base.views.work'),
                       )
