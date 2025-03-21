from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Includes default auth URLs
    path('logout/', auth_views.LogoutView.as_view(next_page='/renewals/login/'), name='logout'),  # Redirect to custom login page
    path('renewals/', include('renewals.urls')),
    path('', RedirectView.as_view(url='renewals/')),  # Redirect root URL to renewals/
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)