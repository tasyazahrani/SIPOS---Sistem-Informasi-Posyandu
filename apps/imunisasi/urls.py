from django.urls import path
from . import views

app_name = 'imunisasi'

urlpatterns = [
    path('', views.imunisasi_list, name='imunisasi_list'),
    path('tambah/', views.imunisasi_create, name='imunisasi_create'),
    path('edit/<int:id>/', views.imunisasi_edit, name='imunisasi_edit'),
    path('hapus/<int:id>/', views.imunisasi_delete, name='imunisasi_delete'),
]