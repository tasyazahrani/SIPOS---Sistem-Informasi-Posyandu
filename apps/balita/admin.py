from django.contrib import admin
from .models import Balita

@admin.register(Balita)
class BalitaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama', 'nik', 'jenis_kelamin', 'nama_ibu', 'created_at']
    list_filter = ['jenis_kelamin', 'status']
    search_fields = ['nama', 'nik', 'nama_ibu']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20