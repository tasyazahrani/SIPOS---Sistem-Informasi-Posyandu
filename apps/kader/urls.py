from django.urls import path
from . import views

app_name = 'kader'

urlpatterns = [
    path('', views.kader_list, name='kader_list'),
    path('tambah/', views.kader_create, name='kader_create'),
    path('edit/<int:id>/', views.kader_edit, name='kader_edit'),
    path('hapus/<int:id>/', views.kader_delete, name='kader_delete'),
    path('reset-password/<int:id>/', views.kader_reset_password, name='kader_reset_password'),
    path('detail/<int:id>/', views.kader_detail, name='kader_detail'),
]