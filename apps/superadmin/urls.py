from django.urls import path
from . import views

app_name = 'superadmin'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('manajemen-user/', views.manajemen_user, name='manajemen_user'),
    path('user/tambah/', views.user_create, name='user_create'),
    path('user/edit/<int:id>/', views.user_edit, name='user_edit'),
    path('user/hapus/<int:id>/', views.user_delete, name='user_delete'),
    path('user/reset-password/<int:id>/', views.user_reset_password, name='user_reset_password'),
    
    # Manajemen Kader
    path('manajemen-kader/', views.manajemen_kader, name='manajemen_kader'),
    path('kader/tambah/', views.kader_create, name='kader_create'),
    path('kader/edit/<int:id>/', views.kader_edit, name='kader_edit'),
    path('kader/hapus/<int:id>/', views.kader_delete, name='kader_delete'),
    path('kader/reset-password/<int:id>/', views.kader_reset_password, name='kader_reset_password'),
    path('kader/detail/<int:id>/', views.kader_detail, name='kader_detail'),
    
    path('manajemen-posyandu/', views.manajemen_posyandu, name='manajemen_posyandu'),
    path('laporan-sistem/', views.laporan_sistem, name='laporan_sistem'),
    path('backup-data/', views.backup_data, name='backup_data'),
    path('pengaturan-sistem/', views.pengaturan_sistem, name='pengaturan_sistem'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
]