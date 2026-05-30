from django.db import models
from apps.balita.models import Balita
from datetime import date, datetime
from django.core.validators import MinValueValidator, MaxValueValidator


class Penimbangan(models.Model):
    STATUS_GIZI_CHOICES = [
        ('Gizi Buruk', 'Gizi Buruk'),
        ('Gizi Kurang', 'Gizi Kurang'),
        ('Gizi Normal', 'Gizi Normal'),
        ('Gizi Lebih', 'Gizi Lebih'),
        ('Resiko Stunting', 'Resiko Stunting'),
    ]
    
    balita = models.ForeignKey(Balita, on_delete=models.CASCADE, related_name='penimbangan')
    tanggal = models.DateField()
    berat_badan = models.FloatField(
        validators=[MinValueValidator(0.1, 'Berat badan minimal 0.1 kg')],
        verbose_name='Berat Badan (kg)'
    )
    tinggi_badan = models.FloatField(
        validators=[MinValueValidator(10, 'Tinggi badan minimal 10 cm')],
        verbose_name='Tinggi Badan (cm)'
    )
    lingkar_kepala = models.FloatField(
        blank=True, 
        null=True,
        validators=[MinValueValidator(20, 'Lingkar kepala minimal 20 cm')],
        verbose_name='Lingkar Kepala (cm)'
    )
    status_gizi = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        choices=STATUS_GIZI_CHOICES,
        verbose_name='Status Gizi'
    )
    keterangan = models.TextField(blank=True, null=True, verbose_name='Keterangan')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def _get_date_object(self, date_value):
        """Konversi string ke date object dengan aman"""
        if date_value is None:
            return None
        if isinstance(date_value, (date, datetime)):
            if isinstance(date_value, datetime):
                return date_value.date()
            return date_value
        if isinstance(date_value, str):
            try:
                return datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_value, '%d/%m/%Y').date()
                except ValueError:
                    return None
        return None
    
    def hitung_umur_bulan(self):
        """Menghitung umur balita dalam bulan pada saat penimbangan"""
        if not self.balita or not self.balita.tanggal_lahir:
            return 0
        
        # Konversi tanggal penimbangan ke date object
        tgl_penimbangan = self._get_date_object(self.tanggal)
        if tgl_penimbangan is None:
            return 0
        
        # Konversi tanggal lahir ke date object jika perlu
        lahir = self.balita.tanggal_lahir
        if isinstance(lahir, str):
            lahir = self._get_date_object(lahir)
        if lahir is None:
            return 0
        
        # Hitung selisih bulan
        bulan = (tgl_penimbangan.year - lahir.year) * 12 + (tgl_penimbangan.month - lahir.month)
        
        # Koreksi jika tanggal belum mencapai tanggal lahir di bulan tersebut
        if tgl_penimbangan.day < lahir.day:
            bulan -= 1
        
        return max(0, bulan)
    
    def hitung_status_gizi(self):
        """Menghitung status gizi berdasarkan umur dan berat badan"""
        umur = self.hitung_umur_bulan()
        
        # Pastikan berat_badan adalah float
        try:
            bb = float(self.berat_badan)
        except (ValueError, TypeError):
            bb = 0
        
        # Jika umur tidak valid, return Normal
        if umur <= 0:
            return "Gizi Normal"
        
        # Standar berdasarkan usia (dalam bulan) dan berat badan (kg)
        # Referensi sederhana, bisa diganti dengan standar WHO yang lebih akurat
        
        # Untuk anak usia 0-24 bulan
        if umur < 24:
            # Ambil bulan ke-n
            bulan_ke = umur
            if bulan_ke <= 3:
                batas_kurang = 4.5
                batas_normal = 6.0
            elif bulan_ke <= 6:
                batas_kurang = 6.0
                batas_normal = 8.0
            elif bulan_ke <= 12:
                batas_kurang = 7.5
                batas_normal = 10.0
            else:
                batas_kurang = 8.5
                batas_normal = 12.0
        else:
            # Untuk anak usia di atas 24 bulan (2 tahun)
            tahun = umur // 12
            if tahun <= 3:
                batas_kurang = 10.0
                batas_normal = 14.0
            elif tahun <= 5:
                batas_kurang = 12.0
                batas_normal = 18.0
            else:
                batas_kurang = 14.0
                batas_normal = 22.0
        
        # Penentuan status gizi
        if bb < (batas_kurang * 0.8):
            return "Gizi Buruk"
        elif bb < batas_kurang:
            return "Gizi Kurang"
        elif bb <= batas_normal:
            return "Gizi Normal"
        else:
            return "Gizi Lebih"
    
    def save(self, *args, **kwargs):
        # Pastikan tanggal adalah date object
        if self.tanggal and isinstance(self.tanggal, str):
            self.tanggal = self._get_date_object(self.tanggal)
        
        # Pastikan berat_badan dan tinggi_badan adalah float
        if self.berat_badan and isinstance(self.berat_badan, str):
            try:
                self.berat_badan = float(self.berat_badan)
            except ValueError:
                self.berat_badan = 0
        
        if self.tinggi_badan and isinstance(self.tinggi_badan, str):
            try:
                self.tinggi_badan = float(self.tinggi_badan)
            except ValueError:
                self.tinggi_badan = 0
        
        # Hitung status gizi hanya jika berat badan ada dan > 0
        if self.berat_badan and self.berat_badan > 0:
            self.status_gizi = self.hitung_status_gizi()
        else:
            self.status_gizi = "Gizi Normal"
        
        super().save(*args, **kwargs)
    
    @property
    def usia_display(self):
        """Menampilkan usia dalam format yang mudah dibaca"""
        bulan = self.hitung_umur_bulan()
        if bulan < 12:
            return f"{bulan} bulan"
        tahun = bulan // 12
        sisa_bulan = bulan % 12
        if sisa_bulan == 0:
            return f"{tahun} tahun"
        return f"{tahun} tahun {sisa_bulan} bulan"
    
    def __str__(self):
        return f"{self.balita.nama} - {self.tanggal}"
    
    class Meta:
        verbose_name = 'Penimbangan'
        verbose_name_plural = 'Data Penimbangan'
        ordering = ['-tanggal']