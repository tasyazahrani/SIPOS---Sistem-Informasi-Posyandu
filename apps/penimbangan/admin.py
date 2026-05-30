from django.contrib import admin
from .models import Penimbangan

@admin.register(Penimbangan)
class PenimbanganAdmin(admin.ModelAdmin):
    list_display = ['id', 'balita', 'tanggal', 'berat_badan', 'tinggi_badan', 'status_gizi']
    list_filter = ['status_gizi', 'tanggal']
    search_fields = ['balita__nama']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20