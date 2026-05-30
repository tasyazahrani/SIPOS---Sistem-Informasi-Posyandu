from django.db import models
from django.core.validators import MinValueValidator


class Jadwal(models.Model):
    JENIS_KEGIATAN_CHOICES = [
        ('Penimbangan', 'Penimbangan Balita'),
        ('Imunisasi', 'Imunisasi'),
        ('Penyuluhan', 'Penyuluhan Kesehatan'),
        ('Kelas Ibu Hamil', 'Kelas Ibu Hamil'),
        ('Pemberian Vitamin', 'Pemberian Vitamin A'),
        ('Lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('Akan Datang', 'Akan Datang'),
        ('Sedang Berlangsung', 'Sedang Berlangsung'),
        ('Selesai', 'Selesai'),
        ('Dibatalkan', 'Dibatalkan'),
    ]
    
    nama_kegiatan = models.CharField(max_length=200, default='Kegiatan Posyandu')
    jenis_kegiatan = models.CharField(max_length=50, choices=JENIS_KEGIATAN_CHOICES, default='Penimbangan')
    tanggal = models.DateField(default='2024-01-01')
    waktu_mulai = models.TimeField(default='08:00')
    waktu_selesai = models.TimeField(default='12:00')
    tempat = models.CharField(max_length=200, default='Posyandu Kemuning')
    petugas = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Akan Datang')
    keterangan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nama_kegiatan} - {self.tanggal}"
    
    class Meta:
        verbose_name = 'Jadwal Posyandu'
        verbose_name_plural = 'Jadwal Posyandu'
        ordering = ['tanggal', 'waktu_mulai']