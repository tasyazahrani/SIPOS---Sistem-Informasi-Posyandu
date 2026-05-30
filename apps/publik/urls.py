from django.urls import path
from . import views

app_name = 'publik'

urlpatterns = [
    path('cek-status/', views.cek_status, name='cek_status'),
    path('jadwal-posyandu/', views.jadwal_posyandu, name='jadwal_posyandu'),
]