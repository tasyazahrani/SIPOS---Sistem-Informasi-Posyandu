from django.db import models
from django.contrib.auth.models import User
from datetime import date, timedelta
from calendar import monthrange


class Balita(models.Model):
    JENIS_KELAMIN_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    
    STATUS_CHOICES = [
        ('aktif', 'Aktif'),
        ('pindah', 'Pindah'),
        ('keluar', 'Keluar'),
    ]
    
    # Relasi ke User (untuk menghubungkan akun orang tua dengan balita)
    user = models.OneToOneField(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='balita',
        verbose_name='Akun Orang Tua'
    )
    
    # Data Dasar Balita
    nama = models.CharField(max_length=100, verbose_name='Nama Lengkap Balita')
    nik = models.CharField(max_length=16, blank=True, null=True, verbose_name='NIK')
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN_CHOICES, verbose_name='Jenis Kelamin')
    tempat_lahir = models.CharField(max_length=100, blank=True, null=True, verbose_name='Tempat Lahir')
    tanggal_lahir = models.DateField(verbose_name='Tanggal Lahir')
    
    # Data Lahir
    berat_lahir = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Berat Lahir (kg)')
    tinggi_lahir = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name='Tinggi Lahir (cm)')
    
    # Data Orang Tua
    nama_ibu = models.CharField(max_length=100, verbose_name='Nama Ibu Kandung')
    nama_ayah = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nama Ayah Kandung')
    no_hp_orang_tua = models.CharField(max_length=15, blank=True, null=True, verbose_name='No. HP Orang Tua')
    
    # Alamat
    alamat = models.TextField(verbose_name='Alamat')
    rt = models.CharField(max_length=3, blank=True, null=True, verbose_name='RT')
    rw = models.CharField(max_length=3, blank=True, null=True, verbose_name='RW')
    desa = models.CharField(max_length=100, blank=True, null=True, verbose_name='Desa/Kelurahan')
    kecamatan = models.CharField(max_length=100, blank=True, null=True, verbose_name='Kecamatan')
    
    # Status
    status = models.CharField(max_length=20, default='aktif', choices=STATUS_CHOICES, verbose_name='Status')
    
    # Catatan
    catatan = models.TextField(blank=True, null=True, verbose_name='Catatan Khusus')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nama
    
    @property
    def usia(self):
        """Menghitung usia balita saat ini"""
        if self.tanggal_lahir:
            today = date.today()
            usia_tahun = today.year - self.tanggal_lahir.year
            usia_bulan = today.month - self.tanggal_lahir.month
            usia_hari = today.day - self.tanggal_lahir.day
            
            if usia_hari < 0:
                usia_bulan -= 1
                last_month = today.replace(day=1) - timedelta(days=1)
                usia_hari += last_month.day
            
            if usia_bulan < 0:
                usia_tahun -= 1
                usia_bulan += 12
            
            if usia_tahun > 0:
                return f"{usia_tahun} tahun {usia_bulan} bulan"
            elif usia_bulan > 0:
                return f"{usia_bulan} bulan {usia_hari} hari"
            else:
                return f"{usia_hari} hari"
        return "-"
    
    @property
    def usia_bulan(self):
        """Menghitung usia dalam bulan"""
        if self.tanggal_lahir:
            today = date.today()
            return (today.year - self.tanggal_lahir.year) * 12 + (today.month - self.tanggal_lahir.month)
        return 0
    
    @property
    def usia_saat_penimbangan(self, tanggal_penimbangan=None):
        """Menghitung usia saat penimbangan (dalam bulan)"""
        if not self.tanggal_lahir:
            return 0
        if not tanggal_penimbangan:
            tanggal_penimbangan = date.today()
        
        bulan = (tanggal_penimbangan.year - self.tanggal_lahir.year) * 12 + (tanggal_penimbangan.month - self.tanggal_lahir.month)
        if tanggal_penimbangan.day < self.tanggal_lahir.day:
            bulan -= 1
        return max(0, bulan)
    
    def cari_user_orang_tua(self):
        """Mencari user orang tua yang cocok dengan data balita"""
        from django.db.models import Q
        
        # Cari berdasarkan NIK
        if self.nik:
            user = User.objects.filter(
                Q(balita__nik=self.nik) |
                Q(email=self.nik) |
                Q(username=self.nik)
            ).first()
            if user:
                return user
        
        # Cari berdasarkan No HP
        if self.no_hp_orang_tua:
            user = User.objects.filter(
                Q(email=self.no_hp_orang_tua) |
                Q(username=self.no_hp_orang_tua)
            ).first()
            if user:
                return user
        
        # Cari berdasarkan nama ibu
        if self.nama_ibu:
            user = User.objects.filter(
                Q(first_name__icontains=self.nama_ibu) |
                Q(username__icontains=self.nama_ibu)
            ).first()
            if user:
                return user
        
        return None
    
    def hubungkan_dengan_user(self):
        """Menghubungkan balita dengan user orang tua yang cocok"""
        user = self.cari_user_orang_tua()
        if user and not self.user:
            from django.contrib.auth.models import Group
            group_ortu, _ = Group.objects.get_or_create(name='Orang Tua')
            if not user.groups.filter(name='Orang Tua').exists():
                user.groups.add(group_ortu)
            self.user = user
            self.save()
            return True
        return False
    
    class Meta:
        verbose_name = 'Balita'
        verbose_name_plural = 'Data Balita'
        ordering = ['-created_at']