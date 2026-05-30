from django.urls import path
from . import views

app_name = 'penimbangan'

urlpatterns = [
    path('', views.penimbangan_list, name='penimbangan_list'),
    path('tambah/', views.penimbangan_create, name='penimbangan_create'),
    path('edit/<int:id>/', views.penimbangan_edit, name='penimbangan_edit'),
    path('hapus/<int:id>/', views.penimbangan_delete, name='penimbangan_delete'),
]