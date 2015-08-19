from django.conf.urls import *
from django.conf import settings
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	(r'^admin/', include(admin.site.urls)),
	(r'^asset/(?P<client>.*)/(?P<automaton>.*)/(?P<slug>.*)/$', 'core.views.asset'),
	(r'^cron/$', 'core.views.cron'),
	(r'^$', 'core.views.index'),
)

if settings.DEBUG:
	urlpatterns += patterns('',
		(
			r'^media/(?P<path>.*)$', 'django.views.static.serve',
			{'document_root': settings.MEDIA_ROOT}
		),
	)
