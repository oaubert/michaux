from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
                       url(r'^$', 'base.views.root'),
                       url(r'^reindex$', 'base.views.reindex'),
                       url(r'^work/$', 'base.views.works'),
                       url(r'^work/(?P<cote>\d+)$', 'base.views.work'),
                       url(r'^work/(?P<cote>\d+)/(?P<type_>.*)$', 'base.views.workextended'),
                       url(r'^compare/(?P<cote1>\d+)/(?P<cote2>\d+)$', 'base.views.compare'),
                       url(r'^complete/(?P<field>\w+)$', 'base.views.complete'),
                       url(r'^selection/tag/$', 'base.views.selection_tag'),
                       url(r'^selection/tag/$', 'base.views.selection_untag'),
                       url(r'^pivot/$', 'base.views.pivot'),
                       url(r'^pivot/collection$', 'base.views.pivotcollection'),
                       url(r'^pivot/dzimages$', 'base.views.pivotdzimages'),
                       url(r'^pivot/image/(?P<cote>\d+)$', 'base.views.pivotimage'),
                       url(r'^pivot/image/(?P<cote>\d+)_files/(?P<level>\d+)/(?P<name>.+).png$', 'base.views.pivotdzimage'),
                       url(r'^pivot/Content/images/(?P<path>.*)', RedirectView.as_view(url=settings.STATIC_URL + 'icons/pivot/%(path)s', permanent=True)),
                       )
