from django.conf.urls.defaults import (patterns, include)
from django.conf import settings
#from django.views.generic.simple import direct_to_template
#from django.views.generic.simple import redirect_to

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# Production URLS
urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^', include('physics_django.magnets.urls')),
    (r'^', include('physics_django.lattice.urls')),
    (r'^', include('physics_django.user.urls')),
	(r'^', include('physics_django.idods.urls')),
    (r'^', include('physics_django.activeinterlock.urls')),
    
    
    # do not use this setting for your production.
    (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),
    (r'^documents/(.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)


# Development URLS
#If we are not in production, then we add in the dev apps
if not settings.PRODUCTION:
    urlpatterns += patterns('',

        (r'^', include('physics_django.magnets.urls')),
        (r'^', include('physics_django.lattice.urls')),
        (r'^', include('physics_django.activeinterlock.urls')),
    )
