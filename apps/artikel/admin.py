from django.contrib import admin
from .models import Artikel

@admin.register(Artikel)
class ArtikelAdmin(admin.ModelAdmin):
    list_display = ['id', 'judul', 'kategori', 'penulis', 'status', 'views', 'published_at']
    list_filter = ['kategori', 'status', 'published_at']
    search_fields = ['judul', 'penulis', 'tags']
    readonly_fields = ['views', 'created_at', 'updated_at']
    list_per_page = 20