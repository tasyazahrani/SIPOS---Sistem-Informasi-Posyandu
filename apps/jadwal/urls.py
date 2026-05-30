from django.urls import path
from . import views

app_name = 'jadwal'

urlpatterns = [
    path('', views.jadwal_list, name='jadwal_list'),
    path('tambah/', views.jadwal_create, name='jadwal_create'),
    path('edit/<int:id>/', views.jadwal_edit, name='jadwal_edit'),
    path('hapus/<int:id>/', views.jadwal_delete, name='jadwal_delete'),
]