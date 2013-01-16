from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^$', 'base.views.root'),
                       url(r'^reindex$', 'base.views.reindex'),
                       url(r'^work/$', 'base.views.works'),
                       url(r'^work/(?P<cote>\d+)/$', 'base.views.work'),
                       )
