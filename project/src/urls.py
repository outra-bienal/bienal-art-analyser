from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
]

if not settings.PRODUCTION:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)