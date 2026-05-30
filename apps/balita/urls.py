from django.urls import path
from . import views

app_name = 'balita'

urlpatterns = [
    path('', views.balita_list, name='balita_list'),
    path('tambah/', views.balita_create, name='balita_create'),
    path('edit/<int:id>/', views.balita_edit, name='balita_edit'),
    path('hapus/<int:id>/', views.balita_delete, name='balita_delete'),
    path('detail/<int:id>/', views.balita_detail, name='balita_detail'), 
]