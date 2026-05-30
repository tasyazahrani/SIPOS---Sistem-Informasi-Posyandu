from django.contrib import admin
from .models import Imunisasi

@admin.register(Imunisasi)
class ImunisasiAdmin(admin.ModelAdmin):
    list_display = ['id', 'balita', 'jenis_imunisasi', 'tanggal', 'status']
    list_filter = ['jenis_imunisasi', 'status', 'tanggal']
    search_fields = ['balita__nama']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20