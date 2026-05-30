from django.urls import include, path
from . import views
from .views import CustomLoginView

app_name = 'core'

urlpatterns = [
    # Halaman Utama
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard-ortu/', views.dashboard_ortu, name='dashboard_ortu'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
    
    # Autentikasi
    path('register/', views.register, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),  # Gunakan custom logout
    
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
