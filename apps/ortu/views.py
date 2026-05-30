from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.contrib.auth import update_session_auth_hash
from apps.balita.models import Balita
from apps.penimbangan.models import Penimbangan
from apps.imunisasi.models import Imunisasi
from apps.artikel.models import Artikel
from datetime import date, timedelta


@login_required
def data_anak(request):
    """Menampilkan data anak untuk orang tua"""
    try:
        balita = request.user.balita
    except:
        balita = None
        messages.info(request, 'Data anak belum terhubung dengan akun Anda. Silakan hubungi admin posyandu.')
    
    if not balita:
        context = {
            'balita': None,
            'total_penimbangan': 0,
            'total_imunisasi': 0,
            'status_normal': 0,
            'total_status': 0,
            'persen_normal': 0,
            'riwayat_penimbangan': [],
            'riwayat_imunisasi': [],
        }
        return render(request, 'ortu/data_anak.html', context)
    
    # Data penimbangan
    riwayat_penimbangan = Penimbangan.objects.filter(balita=balita).order_by('-tanggal')[:5]
    total_penimbangan = Penimbangan.objects.filter(balita=balita).count()
    
    # Data imunisasi
    riwayat_imunisasi = Imunisasi.objects.filter(balita=balita).order_by('-tanggal')[:5]
    total_imunisasi = Imunisasi.objects.filter(balita=balita).count()
    
    # Status gizi
    penimbangan_terakhir = Penimbangan.objects.filter(balita=balita).order_by('-tanggal').first()
    if penimbangan_terakhir and penimbangan_terakhir.status_gizi:
        status = penimbangan_terakhir.status_gizi
        if 'Normal' in status:
            status_normal = 1
        else:
            status_normal = 0
    else:
        status_normal = 0
    
    context = {
        'balita': balita,
        'total_penimbangan': total_penimbangan,
        'total_imunisasi': total_imunisasi,
        'status_normal': status_normal,
        'total_status': 1 if status_normal > 0 else 0,
        'persen_normal': 100 if status_normal > 0 else 0,
        'riwayat_penimbangan': riwayat_penimbangan,
        'riwayat_imunisasi': riwayat_imunisasi,
    }
    return render(request, 'ortu/data_anak.html', context)


@login_required
def riwayat_penimbangan(request):
    """Menampilkan riwayat penimbangan lengkap untuk orang tua"""
    try:
        balita = request.user.balita
    except:
        balita = None
        messages.info(request, 'Data anak belum terhubung dengan akun Anda. Silakan hubungi admin posyandu.')
        return render(request, 'ortu/riwayat_penimbangan.html', {'balita': None, 'penimbangan_list': []})
    
    # Ambil semua data penimbangan
    penimbangan_list = Penimbangan.objects.filter(balita=balita).order_by('-tanggal')
    
    # Filter berdasarkan tahun
    tahun = request.GET.get('tahun')
    if tahun:
        penimbangan_list = penimbangan_list.filter(tanggal__year=tahun)
    
    # Pagination
    paginator = Paginator(penimbangan_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistik
    total_penimbangan = penimbangan_list.count()
    
    # Rata-rata berat dan tinggi
    if total_penimbangan > 0:
        total_berat = sum([float(p.berat_badan) for p in penimbangan_list])
        total_tinggi = sum([float(p.tinggi_badan) for p in penimbangan_list])
        rata_berat = round(total_berat / total_penimbangan, 2)
        rata_tinggi = round(total_tinggi / total_penimbangan, 2)
    else:
        rata_berat = 0
        rata_tinggi = 0
    
    # Penimbangan terbaru dan terlama
    penimbangan_terbaru = penimbangan_list.first()
    penimbangan_terlama = penimbangan_list.last()
    
    # Data untuk grafik
    chart_penimbangan = penimbangan_list.order_by('tanggal')
    chart_labels = [p.tanggal.strftime('%b %Y') for p in chart_penimbangan]
    chart_berat = [float(p.berat_badan) for p in chart_penimbangan]
    chart_tinggi = [float(p.tinggi_badan) for p in chart_penimbangan]
    
    # Tahun untuk filter
    tahun_list = Penimbangan.objects.filter(balita=balita).dates('tanggal', 'year')
    
    context = {
        'balita': balita,
        'penimbangan_list': page_obj,
        'total_penimbangan': total_penimbangan,
        'rata_berat': rata_berat,
        'rata_tinggi': rata_tinggi,
        'penimbangan_terbaru': penimbangan_terbaru,
        'penimbangan_terlama': penimbangan_terlama,
        'tahun_terpilih': tahun,
        'tahun_list': tahun_list,
        'chart_labels': chart_labels,
        'chart_berat': chart_berat,
        'chart_tinggi': chart_tinggi,
    }
    return render(request, 'ortu/riwayat_penimbangan.html', context)


@login_required
def riwayat_imunisasi(request):
    """Menampilkan riwayat imunisasi lengkap untuk orang tua"""
    try:
        balita = request.user.balita
    except:
        balita = None
        messages.info(request, 'Data anak belum terhubung dengan akun Anda. Silakan hubungi admin posyandu.')
        return render(request, 'ortu/riwayat_imunisasi.html', {'balita': None, 'imunisasi_list': []})
    
    # Ambil semua data imunisasi
    imunisasi_list = Imunisasi.objects.filter(balita=balita).order_by('-tanggal')
    
    # Filter berdasarkan tahun
    tahun = request.GET.get('tahun')
    if tahun:
        imunisasi_list = imunisasi_list.filter(tanggal__year=tahun)
    
    # Filter berdasarkan status
    status = request.GET.get('status')
    if status:
        imunisasi_list = imunisasi_list.filter(status=status)
    
    # Pagination
    paginator = Paginator(imunisasi_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistik
    total_imunisasi = imunisasi_list.count()
    imunisasi_sudah = imunisasi_list.filter(status='Sudah').count()
    imunisasi_belum = imunisasi_list.filter(status='Belum').count()
    imunisasi_dijadwalkan = imunisasi_list.filter(status='Dijadwalkan').count()
    imunisasi_terlewat = imunisasi_list.filter(status='Terlewat').count()
    persen_selesai = round((imunisasi_sudah / total_imunisasi * 100) if total_imunisasi > 0 else 0)
    
    # Imunisasi berikutnya
    today = date.today()
    imunisasi_berikutnya = Imunisasi.objects.filter(
        balita=balita, 
        tanggal__gte=today
    ).order_by('tanggal').first()
    
    # Imunisasi yang terlewat
    imunisasi_terlewat_list = Imunisasi.objects.filter(
        balita=balita,
        status='Terlewat'
    ).order_by('-tanggal')
    
    # Tahun untuk filter
    tahun_list = Imunisasi.objects.filter(balita=balita).dates('tanggal', 'year')
    
    context = {
        'balita': balita,
        'imunisasi_list': page_obj,
        'total_imunisasi': total_imunisasi,
        'imunisasi_sudah': imunisasi_sudah,
        'imunisasi_belum': imunisasi_belum,
        'imunisasi_dijadwalkan': imunisasi_dijadwalkan,
        'imunisasi_terlewat': imunisasi_terlewat,
        'persen_selesai': persen_selesai,
        'imunisasi_berikutnya': imunisasi_berikutnya,
        'imunisasi_terlewat_list': imunisasi_terlewat_list,
        'tahun_terpilih': tahun,
        'status_terpilih': status,
        'tahun_list': tahun_list,
    }
    return render(request, 'ortu/riwayat_imunisasi.html', context)


@login_required
def artikel_edukasi(request):
    """Menampilkan daftar artikel edukasi untuk orang tua"""
    artikel_list = Artikel.objects.filter(status='published').order_by('-published_at')
    
    # Filter berdasarkan kategori
    kategori = request.GET.get('kategori')
    if kategori:
        artikel_list = artikel_list.filter(kategori=kategori)
    
    # Filter berdasarkan pencarian
    search = request.GET.get('search')
    if search:
        artikel_list = artikel_list.filter(
            models.Q(judul__icontains=search) | 
            models.Q(konten__icontains=search) |
            models.Q(tags__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(artikel_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Kategori untuk filter
    categories = Artikel.KATEGORI_CHOICES
    
    # Artikel populer (views terbanyak)
    artikel_populer = Artikel.objects.filter(status='published').order_by('-views')[:5]
    
    # Artikel terbaru
    artikel_terbaru = Artikel.objects.filter(status='published').order_by('-published_at')[:5]
    
    context = {
        'artikel_list': page_obj,
        'categories': categories,
        'selected_kategori': kategori,
        'search': search,
        'artikel_populer': artikel_populer,
        'artikel_terbaru': artikel_terbaru,
    }
    return render(request, 'ortu/artikel_edukasi.html', context)


@login_required
def artikel_detail(request, id):
    """Menampilkan detail artikel"""
    artikel = get_object_or_404(Artikel, id=id, status='published')
    
    # Increase view count
    artikel.views += 1
    artikel.save(update_fields=['views'])
    
    # Artikel terkait (kategori yang sama)
    artikel_terkait = Artikel.objects.filter(
        kategori=artikel.kategori, 
        status='published'
    ).exclude(id=artikel.id)[:3]
    
    context = {
        'artikel': artikel,
        'artikel_terkait': artikel_terkait,
    }
    return render(request, 'ortu/artikel_detail.html', context)


@login_required
def jadwal_imunisasi(request):
    """Menampilkan jadwal imunisasi untuk orang tua"""
    try:
        balita = request.user.balita
    except:
        balita = None
        messages.info(request, 'Data anak belum terhubung dengan akun Anda. Silakan hubungi admin posyandu.')
        return render(request, 'ortu/jadwal_imunisasi.html', {'balita': None})
    
    today = date.today()
    
    # Imunisasi yang akan datang (Dijadwalkan atau Belum, tanggal >= hari ini)
    jadwal_mendatang = Imunisasi.objects.filter(
        balita=balita,
        tanggal__gte=today
    ).exclude(status='Sudah').order_by('tanggal')
    
    # Imunisasi yang terlewat (tanggal < hari ini, status belum/dijadwalkan)
    jadwal_terlewat = Imunisasi.objects.filter(
        balita=balita,
        tanggal__lt=today,
        status__in=['Belum', 'Dijadwalkan']
    ).order_by('-tanggal')
    
    # Rekomendasi imunisasi berdasarkan usia
    rekomendasi = []
    if balita and balita.tanggal_lahir:
        usia_bulan = (today.year - balita.tanggal_lahir.year) * 12 + (today.month - balita.tanggal_lahir.month)
        if today.day < balita.tanggal_lahir.day:
            usia_bulan -= 1
        
        # Daftar imunisasi rekomendasi berdasarkan usia
        jadwal_rekomendasi = [
            {'usia': 0, 'nama': 'Hepatitis B 0', 'keterangan': 'Saat lahir, 24 jam setelah lahir'},
            {'usia': 1, 'nama': 'BCG', 'keterangan': 'Usia < 3 bulan'},
            {'usia': 2, 'nama': 'DPT-HB-Hib 1', 'keterangan': 'Usia 2 bulan'},
            {'usia': 2, 'nama': 'Polio 1', 'keterangan': 'Usia 2 bulan'},
            {'usia': 3, 'nama': 'DPT-HB-Hib 2', 'keterangan': 'Usia 3 bulan'},
            {'usia': 3, 'nama': 'Polio 2', 'keterangan': 'Usia 3 bulan'},
            {'usia': 4, 'nama': 'DPT-HB-Hib 3', 'keterangan': 'Usia 4 bulan'},
            {'usia': 4, 'nama': 'Polio 3', 'keterangan': 'Usia 4 bulan'},
            {'usia': 9, 'nama': 'Campak', 'keterangan': 'Usia 9 bulan'},
            {'usia': 18, 'nama': 'DPT-HB-Hib (Booster)', 'keterangan': 'Usia 18 bulan'},
            {'usia': 18, 'nama': 'Campak (Booster)', 'keterangan': 'Usia 18 bulan'},
        ]
        
        # Cek imunisasi yang sudah dilakukan
        imunisasi_dilakukan = Imunisasi.objects.filter(
            balita=balita,
            status='Sudah'
        ).values_list('jenis_imunisasi', flat=True)
        
        for jadwal in jadwal_rekomendasi:
            if jadwal['usia'] <= usia_bulan:
                # Cek apakah sudah dilakukan
                sudah = any(jadwal['nama'].lower() in imu.lower() for imu in imunisasi_dilakukan)
                if not sudah:
                    rekomendasi.append({
                        'nama': jadwal['nama'],
                        'usia': jadwal['usia'],
                        'usia_bulan': jadwal['usia'],
                        'keterangan': jadwal['keterangan'],
                        'status': 'Belum'
                    })
    
    # Statistik
    total_imunisasi = Imunisasi.objects.filter(balita=balita).count()
    imunisasi_sudah = Imunisasi.objects.filter(balita=balita, status='Sudah').count()
    imunisasi_belum = Imunisasi.objects.filter(balita=balita, status='Belum').count()
    imunisasi_terlewat = jadwal_terlewat.count()
    persen_selesai = round((imunisasi_sudah / total_imunisasi * 100) if total_imunisasi > 0 else 0)
    
    context = {
        'balita': balita,
        'jadwal_mendatang': jadwal_mendatang,
        'jadwal_terlewat': jadwal_terlewat,
        'rekomendasi': rekomendasi,
        'total_imunisasi': total_imunisasi,
        'imunisasi_sudah': imunisasi_sudah,
        'imunisasi_belum': imunisasi_belum,
        'imunisasi_terlewat': imunisasi_terlewat,
        'persen_selesai': persen_selesai,
        'usia_bulan': (date.today().year - balita.tanggal_lahir.year) * 12 + (date.today().month - balita.tanggal_lahir.month) if balita.tanggal_lahir else 0,
    }
    return render(request, 'ortu/jadwal_imunisasi.html', context)


@login_required
def pengaturan_ortu(request):
    """Halaman pengaturan untuk orang tua"""
    user = request.user
    
    # Ambil data balita
    try:
        balita = request.user.balita
    except:
        balita = None
    
    if request.method == 'POST':
        action = request.POST.get('action', 'profile')
        
        if action == 'profile':
            # Update profil orang tua
            first_name = request.POST.get('first_name')
            email = request.POST.get('email')
            no_hp = request.POST.get('no_hp')
            
            if first_name:
                user.first_name = first_name
            if email:
                user.email = email
            user.save()
            
            # Update no HP balita jika ada
            if balita and no_hp:
                balita.no_hp_orang_tua = no_hp
                balita.save()
            
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('ortu:pengaturan_ortu')
        
        elif action == 'password':
            # Update password
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not user.check_password(old_password):
                messages.error(request, 'Password lama salah!')
                return redirect('ortu:pengaturan_ortu')
            
            if new_password1 != new_password2:
                messages.error(request, 'Password baru tidak cocok!')
                return redirect('ortu:pengaturan_ortu')
            
            if len(new_password1) < 8:
                messages.error(request, 'Password minimal 8 karakter!')
                return redirect('ortu:pengaturan_ortu')
            
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password berhasil diubah!')
            return redirect('ortu:pengaturan_ortu')
        
        elif action == 'notification':
            # Update preferensi notifikasi
            email_notif = request.POST.get('email_notif') == 'on'
            sms_notif = request.POST.get('sms_notif') == 'on'
            
            request.session['email_notif'] = email_notif
            request.session['sms_notif'] = sms_notif
            
            messages.success(request, 'Preferensi notifikasi berhasil diperbarui!')
            return redirect('ortu:pengaturan_ortu')
    
    # Get notification preferences from session
    email_notif = request.session.get('email_notif', True)
    sms_notif = request.session.get('sms_notif', False)
    
    # Data untuk ditampilkan
    context = {
        'user': user,
        'balita': balita,
        'email_notif': email_notif,
        'sms_notif': sms_notif,
    }
    return render(request, 'ortu/pengaturan.html', context)