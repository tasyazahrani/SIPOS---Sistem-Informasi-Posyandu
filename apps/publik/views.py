from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from apps.balita.models import Balita
from apps.penimbangan.models import Penimbangan
from apps.jadwal.models import Jadwal
from datetime import datetime, date


def cek_status(request):
    """Halaman publik untuk cek status gizi balita"""
    hasil = None
    balita = None
    pesan_error = None
    
    if request.method == 'POST':
        keyword = request.POST.get('keyword', '').strip()
        
        if keyword:
            # Cari balita berdasarkan NIK atau nama
            balita_list = Balita.objects.filter(
                Q(nik=keyword) | Q(nama__icontains=keyword)
            )
            
            if balita_list.exists():
                balita = balita_list.first()
                
                # Ambil penimbangan terakhir
                penimbangan_terakhir = Penimbangan.objects.filter(balita=balita).order_by('-tanggal').first()
                
                # Hitung usia
                today = date.today()
                if balita.tanggal_lahir:
                    usia_tahun = today.year - balita.tanggal_lahir.year
                    usia_bulan = today.month - balita.tanggal_lahir.month
                    if today.day < balita.tanggal_lahir.day:
                        usia_bulan -= 1
                    if usia_bulan < 0:
                        usia_tahun -= 1
                        usia_bulan += 12
                    
                    if usia_tahun > 0:
                        usia_display = f"{usia_tahun} tahun {usia_bulan} bulan"
                    else:
                        usia_display = f"{usia_bulan} bulan"
                else:
                    usia_display = "-"
                
                # Tentukan status dan rekomendasi
                status_gizi = penimbangan_terakhir.status_gizi if penimbangan_terakhir else "Belum ada data"
                rekomendasi = ""
                warna_status = ""
                icon = ""
                
                if status_gizi == "Normal":
                    warna_status = "text-green-600"
                    bg_status = "bg-green-100"
                    icon = "✅"
                    rekomendasi = "Pertumbuhan anak baik. Pertahankan pola makan sehat dan rutin kontrol ke posyandu."
                elif status_gizi == "Gizi Kurang":
                    warna_status = "text-yellow-600"
                    bg_status = "bg-yellow-100"
                    icon = "⚠️"
                    rekomendasi = "Perlu peningkatan asupan nutrisi. Konsultasikan dengan kader posyandu untuk menu tambahan."
                elif status_gizi == "Gizi Buruk":
                    warna_status = "text-red-600"
                    bg_status = "bg-red-100"
                    icon = "🚨"
                    rekomendasi = "Segera bawa anak ke puskesmas atau tenaga kesehatan terdekat untuk penanganan lebih lanjut."
                elif status_gizi == "Gizi Lebih":
                    warna_status = "text-orange-600"
                    bg_status = "bg-orange-100"
                    icon = "⚠️"
                    rekomendasi = "Perhatikan pola makan dan tingkatkan aktivitas fisik. Konsultasikan dengan tenaga kesehatan."
                else:
                    warna_status = "text-gray-600"
                    bg_status = "bg-gray-100"
                    icon = "ℹ️"
                    rekomendasi = "Silakan lakukan penimbangan rutin di posyandu terdekat."
                
                hasil = {
                    'balita': balita,
                    'usia_display': usia_display,
                    'penimbangan_terakhir': penimbangan_terakhir,
                    'status_gizi': status_gizi,
                    'rekomendasi': rekomendasi,
                    'warna_status': warna_status,
                    'bg_status': bg_status,
                    'icon': icon,
                }
            else:
                pesan_error = f"Data dengan NIK/Nama '{keyword}' tidak ditemukan. Pastikan data sudah terdaftar di posyandu."
    
    context = {
        'hasil': hasil,
        'pesan_error': pesan_error,
    }
    return render(request, 'publik/cek_status.html', context)


def jadwal_posyandu(request):
    """Halaman publik untuk melihat jadwal posyandu"""
    today = date.today()
    
    # Ambil semua jadwal yang akan datang (hari ini atau setelahnya)
    jadwal_mendatang = Jadwal.objects.filter(
        tanggal__gte=today,
        status='Akan Datang'
    ).order_by('tanggal', 'waktu_mulai')[:10]
    
    # Ambil jadwal terbaru (yang sudah lewat)
    jadwal_terlewat = Jadwal.objects.filter(
        tanggal__lt=today,
        status='Akan Datang'
    ).order_by('-tanggal')[:5]
    
    # Ambil jadwal yang sedang berlangsung
    jadwal_berlangsung = Jadwal.objects.filter(
        tanggal=today,
        status='Sedang Berlangsung'
    ).order_by('waktu_mulai')
    
    # Semua jadwal untuk bulan ini
    from calendar import monthrange
    first_day = today.replace(day=1)
    last_day = today.replace(day=monthrange(today.year, today.month)[1])
    jadwal_bulan_ini = Jadwal.objects.filter(
        tanggal__gte=first_day,
        tanggal__lte=last_day
    ).order_by('tanggal', 'waktu_mulai')
    
    # Filter berdasarkan bulan
    bulan = request.GET.get('bulan')
    tahun = request.GET.get('tahun')
    if bulan and tahun:
        try:
            bulan_int = int(bulan)
            tahun_int = int(tahun)
            start = date(tahun_int, bulan_int, 1)
            end = date(tahun_int, bulan_int, monthrange(tahun_int, bulan_int)[1])
            jadwal_bulan_ini = Jadwal.objects.filter(
                tanggal__gte=start,
                tanggal__lte=end
            ).order_by('tanggal', 'waktu_mulai')
        except:
            pass
    
    # Daftar bulan untuk filter
    from calendar import month_name
    bulan_list = [(i, month_name[i]) for i in range(1, 13)]
    tahun_list = [2023, 2024, 2025, 2026, 2027]
    
    context = {
        'jadwal_mendatang': jadwal_mendatang,
        'jadwal_terlewat': jadwal_terlewat,
        'jadwal_berlangsung': jadwal_berlangsung,
        'jadwal_bulan_ini': jadwal_bulan_ini,
        'bulan_list': bulan_list,
        'tahun_list': tahun_list,
        'today': today,
    }
    return render(request, 'publik/jadwal_posyandu.html', context)