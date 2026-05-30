from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.core.views import home, dashboard, dashboard_ortu, register, pengaturan, CustomLoginView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Halaman Utama
    path('', home, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard-ortu/', dashboard_ortu, name='dashboard_ortu'),
    path('pengaturan/', pengaturan, name='pengaturan'),
    path('register/', register, name='register'),
    
    # Autentikasi dengan CustomLoginView
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    
    # Apps URLs
    path('balita/', include('apps.balita.urls')),
    path('penimbangan/', include('apps.penimbangan.urls')),
    path('imunisasi/', include('apps.imunisasi.urls')),
    path('jadwal/', include('apps.jadwal.urls')),
    path('artikel/', include('apps.artikel.urls')),
    path('kader/', include('apps.kader.urls')),
    path('laporan/', include('apps.laporan.urls')),
    path('ortu/', include('apps.ortu.urls')),
    path('superadmin/', include('apps.superadmin.urls')),
    path('publik/', include('apps.publik.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)