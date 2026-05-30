from django.urls import path
from . import views

app_name = 'laporan'

urlpatterns = [
    path('', views.laporan_index, name='laporan_index'),
    path('export/excel/', views.laporan_export_excel, name='laporan_export_excel'),
    path('export/pdf/', views.laporan_export_pdf, name='laporan_export_pdf'),
]