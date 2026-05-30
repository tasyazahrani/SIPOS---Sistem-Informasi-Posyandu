from django.urls import path
from . import views

app_name = 'ortu'

urlpatterns = [
    path('data-anak/', views.data_anak, name='data_anak'),
    path('riwayat-penimbangan/', views.riwayat_penimbangan, name='riwayat_penimbangan'),
    path('riwayat-imunisasi/', views.riwayat_imunisasi, name='riwayat_imunisasi'),
    path('artikel-edukasi/', views.artikel_edukasi, name='artikel_edukasi'),
    path('artikel-detail/<int:id>/', views.artikel_detail, name='artikel_detail'),
    path('jadwal-imunisasi/', views.jadwal_imunisasi, name='jadwal_imunisasi'),
    path('pengaturan/', views.pengaturan_ortu, name='pengaturan_ortu'),
]