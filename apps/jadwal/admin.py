from django.contrib import admin
from .models import Jadwal

@admin.register(Jadwal)
class JadwalAdmin(admin.ModelAdmin):
    list_display = ['id', 'nama_kegiatan', 'jenis_kegiatan', 'tanggal', 'waktu_mulai', 'tempat', 'status']
    list_filter = ['jenis_kegiatan', 'status', 'tanggal']
    search_fields = ['nama_kegiatan', 'tempat']
    list_per_page = 20