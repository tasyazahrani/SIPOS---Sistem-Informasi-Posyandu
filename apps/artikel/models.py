from django.db import models
from django.utils import timezone


class Artikel(models.Model):
    KATEGORI_CHOICES = [
        ('Kesehatan Balita', 'Kesehatan Balita'),
        ('Gizi & Nutrisi', 'Gizi & Nutrisi'),
        ('Imunisasi', 'Imunisasi'),
        ('Tumbuh Kembang', 'Tumbuh Kembang'),
        ('Penyakit Anak', 'Penyakit Anak'),
        ('Ibu & Anak', 'Ibu & Anak'),
        ('Lainnya', 'Lainnya'),
    ]
    
    judul = models.CharField(max_length=200, verbose_name='Judul Artikel')
    kategori = models.CharField(max_length=50, choices=KATEGORI_CHOICES, default='Kesehatan Balita', verbose_name='Kategori')
    konten = models.TextField(verbose_name='Isi Artikel')
    ringkasan = models.TextField(max_length=500, blank=True, null=True, verbose_name='Ringkasan')
    gambar = models.ImageField(upload_to='artikel/', blank=True, null=True, verbose_name='Gambar')
    penulis = models.CharField(max_length=100, default='Admin SIPOS', verbose_name='Penulis')
    tags = models.CharField(max_length=200, blank=True, null=True, verbose_name='Tags (pisahkan dengan koma)')
    views = models.IntegerField(default=0, verbose_name='Jumlah Dibaca')
    status = models.CharField(max_length=20, default='published', choices=[('draft', 'Draft'), ('published', 'Published')], verbose_name='Status')
    published_at = models.DateTimeField(default=timezone.now, verbose_name='Tanggal Publikasi')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.judul
    
    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])
    
    class Meta:
        verbose_name = 'Artikel'
        verbose_name_plural = 'Artikel Edukasi'
        ordering = ['-published_at']