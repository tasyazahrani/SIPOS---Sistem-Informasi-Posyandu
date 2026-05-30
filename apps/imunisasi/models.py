from django.db import models
from apps.balita.models import Balita


class Imunisasi(models.Model):
    JENIS_IMUNISASI_CHOICES = [
        ('BCG', 'BCG'),
        ('DPT', 'DPT'),
        ('Polio', 'Polio'),
        ('Campak', 'Campak'),
        ('Hepatitis B', 'Hepatitis B'),
        ('Hib', 'Hib'),
        ('Rotavirus', 'Rotavirus'),
        ('PCV', 'PCV'),
        ('IPV', 'IPV'),
        ('JE', 'JE'),
        ('MMR', 'MMR'),
        ('Td', 'Td'),
        ('HPV', 'HPV'),
        ('Lainnya', 'Lainnya'),
    ]
    
    STATUS_CHOICES = [
        ('Sudah', 'Sudah'),
        ('Belum', 'Belum'),
        ('Terlewat', 'Terlewat'),
        ('Dijadwalkan', 'Dijadwalkan'),
    ]
    
    balita = models.ForeignKey(Balita, on_delete=models.CASCADE, related_name='imunisasi')
    jenis_imunisasi = models.CharField(max_length=50, choices=JENIS_IMUNISASI_CHOICES, default='BCG')
    tanggal = models.DateField()
    usia_saat_imunisasi = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Belum')
    tempat = models.CharField(max_length=200, blank=True, null=True)
    keterangan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if self.balita and self.balita.tanggal_lahir and self.tanggal:
            from datetime import date
            if isinstance(self.tanggal, str):
                from datetime import datetime
                tgl_imunisasi = datetime.strptime(self.tanggal, '%Y-%m-%d').date()
            else:
                tgl_imunisasi = self.tanggal
            
            lahir = self.balita.tanggal_lahir
            usia_bulan = (tgl_imunisasi.year - lahir.year) * 12 + (tgl_imunisasi.month - lahir.month)
            if tgl_imunisasi.day < lahir.day:
                usia_bulan -= 1
            self.usia_saat_imunisasi = max(0, usia_bulan)
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.balita.nama} - {self.get_jenis_imunisasi_display()} - {self.tanggal}"
    
    class Meta:
        verbose_name = 'Imunisasi'
        verbose_name_plural = 'Data Imunisasi'
        ordering = ['-tanggal']