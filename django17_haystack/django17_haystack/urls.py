from django.conf.urls import patterns, include, url
from django.contrib import admin

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

urlpatterns = patterns('',

    #url(r'^$', lambda request: HttpResponseRedirect(reverse('search_view')), name='redirect_search'),
    url(r'^$', lambda request: HttpResponseRedirect('/search/'), name='redirect_search'),

    url(r'^search/', include('haystack.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^mysearch/', include('mysearch.urls')),

)
