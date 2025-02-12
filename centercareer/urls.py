"""
URL configuration for centercareer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls import handler404, handler500, handler403
from .views import custom_page_not_found, custom_server_error, custom_permission_denied
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, VacancySitemap, EventSitemap

from django.views.generic import TemplateView

sitemaps = {
    "static": StaticViewSitemap,
    "vacancies": VacancySitemap,
    "events": EventSitemap,
}


urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="app/robots.txt", content_type="text/plain"),
    ),
    path("admin/", admin.site.urls),
    path("", include("app.urls")),
]

handler404 = custom_page_not_found
handler500 = custom_server_error
handler403 = custom_permission_denied

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
