from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.views.generic import RedirectView
admin.autodiscover()

urlpatterns = patterns('',
                       url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': settings.STATIC_URL + 'icons/favicon.ico'}),
                       url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
                       url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
                       url(r'^$', RedirectView.as_view(url='/base/')),
                       url(r'^base/', include('base.urls')),
                       url(r'^admin/', include(admin.site.urls)),
                       url(r'^search/', include('haystack.urls')),
                       url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
                       url(r'^', include('coop_tag.urls')),
)
