from django.urls import path
from . import views

app_name = 'artikel'

urlpatterns = [
    path('', views.artikel_list, name='artikel_list'),
    path('detail/<int:id>/', views.artikel_detail, name='artikel_detail'),
    path('tambah/', views.artikel_create, name='artikel_create'),
    path('edit/<int:id>/', views.artikel_edit, name='artikel_edit'),
    path('hapus/<int:id>/', views.artikel_delete, name='artikel_delete'),
]