from django.db import models

class Laporan(models.Model):
    bulan = models.IntegerField()
    tahun = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Laporan'
        verbose_name_plural = 'Laporan Bulanan'
        ordering = ['-tahun', '-bulan']