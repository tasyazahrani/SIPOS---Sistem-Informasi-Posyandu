from datetime import date, timedelta
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Q, Avg
from django.contrib.auth.models import User, Group

from .models import Balita
from apps.penimbangan.models import Penimbangan
from apps.imunisasi.models import Imunisasi


@login_required
def balita_list(request):
    """Menampilkan daftar semua balita dengan pagination dan filter"""
    balita_list = Balita.objects.all().order_by('-created_at')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        balita_list = balita_list.filter(
            Q(nama__icontains=search) |
            Q(nik__icontains=search) |
            Q(nama_ibu__icontains=search)
        )
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        balita_list = balita_list.filter(status=status)
    
    # Pagination (10 data per halaman)
    paginator = Paginator(balita_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'balita_list': page_obj,
        'search': search,
        'status_filter': status,
    }
    return render(request, 'balita/list.html', context)


@login_required
def balita_create(request):
    """Form untuk menambah balita baru"""
    if request.method == 'POST':
        try:
            nama = request.POST.get('nama')
            nik = request.POST.get('nik')
            jenis_kelamin = request.POST.get('jenis_kelamin')
            tempat_lahir = request.POST.get('tempat_lahir')
            tanggal_lahir = request.POST.get('tanggal_lahir')
            berat_lahir = request.POST.get('berat_lahir')
            tinggi_lahir = request.POST.get('tinggi_lahir')
            nama_ibu = request.POST.get('nama_ibu')
            nama_ayah = request.POST.get('nama_ayah')
            alamat = request.POST.get('alamat')
            no_hp = request.POST.get('no_hp_orang_tua')
            rt = request.POST.get('rt')
            rw = request.POST.get('rw')
            desa = request.POST.get('desa')
            kecamatan = request.POST.get('kecamatan')
            status = request.POST.get('status', 'aktif')
            
            # Validasi field wajib
            if not nama or not tanggal_lahir or not jenis_kelamin or not nama_ibu:
                messages.error(request, 'Mohon isi field yang wajib diisi!')
                return render(request, 'balita/form.html')
            
            # Validasi format tanggal
            try:
                if isinstance(tanggal_lahir, str):
                    tanggal_lahir = date.fromisoformat(tanggal_lahir)
            except ValueError:
                messages.error(request, 'Format tanggal lahir tidak valid!')
                return render(request, 'balita/form.html')
            
            # Cari user orang tua yang cocok berdasarkan NIK atau No HP
            user = None
            if nik:
                user = User.objects.filter(
                    Q(balita__nik=nik) |
                    Q(username=nik) | 
                    Q(email=nik)
                ).first()
            
            if not user and no_hp:
                user = User.objects.filter(
                    Q(username=no_hp) | 
                    Q(email=no_hp)
                ).first()
            
            # Buat balita baru
            balita = Balita.objects.create(
                nama=nama,
                nik=nik if nik else None,
                jenis_kelamin=jenis_kelamin,
                tempat_lahir=tempat_lahir if tempat_lahir else None,
                tanggal_lahir=tanggal_lahir,
                berat_lahir=berat_lahir if berat_lahir else None,
                tinggi_lahir=tinggi_lahir if tinggi_lahir else None,
                nama_ibu=nama_ibu,
                nama_ayah=nama_ayah if nama_ayah else None,
                alamat=alamat,
                no_hp_orang_tua=no_hp if no_hp else None,
                rt=rt if rt else None,
                rw=rw if rw else None,
                desa=desa if desa else None,
                kecamatan=kecamatan if kecamatan else None,
                status=status,
                user=user if user else None
            )
            
            # Jika user ditemukan, pastikan memiliki group Orang Tua
            if user:
                group_ortu, _ = Group.objects.get_or_create(name='Orang Tua')
                if not user.groups.filter(name='Orang Tua').exists():
                    user.groups.add(group_ortu)
                messages.success(request, f'Data balita {nama} berhasil ditambahkan dan terhubung dengan akun {user.username}!')
            else:
                messages.success(request, f'Data balita {nama} berhasil ditambahkan!')
                if no_hp or nik:
                    messages.info(request, 'Orang tua dapat menghubungkan akun menggunakan NIK atau No. HP saat registrasi.')
            
            return redirect('balita:balita_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'balita/form.html')


@login_required
def balita_edit(request, id):
    """Form untuk mengedit data balita"""
    balita = get_object_or_404(Balita, id=id)
    
    if request.method == 'POST':
        try:
            balita.nama = request.POST.get('nama')
            balita.nik = request.POST.get('nik') or None
            balita.jenis_kelamin = request.POST.get('jenis_kelamin')
            balita.tempat_lahir = request.POST.get('tempat_lahir') or None
            balita.tanggal_lahir = request.POST.get('tanggal_lahir')
            balita.berat_lahir = request.POST.get('berat_lahir') or None
            balita.tinggi_lahir = request.POST.get('tinggi_lahir') or None
            balita.nama_ibu = request.POST.get('nama_ibu')
            balita.nama_ayah = request.POST.get('nama_ayah') or None
            balita.alamat = request.POST.get('alamat')
            balita.no_hp_orang_tua = request.POST.get('no_hp_orang_tua') or None
            balita.rt = request.POST.get('rt') or None
            balita.rw = request.POST.get('rw') or None
            balita.desa = request.POST.get('desa') or None
            balita.kecamatan = request.POST.get('kecamatan') or None
            balita.status = request.POST.get('status', 'aktif')
            balita.save()
            
            messages.success(request, f'Data balita {balita.nama} berhasil diupdate!')
            return redirect('balita:balita_list')
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'balita/form.html', {'balita': balita})


@login_required
def balita_delete(request, id):
    """Menghapus data balita"""
    balita = get_object_or_404(Balita, id=id)
    
    if request.method == 'POST':
        nama_balita = balita.nama
        balita.delete()
        messages.success(request, f'Data balita {nama_balita} berhasil dihapus!')
        return redirect('balita:balita_list')
    
    return render(request, 'balita/confirm_delete.html', {'balita': balita})


@login_required
def balita_detail(request, id):
    """Menampilkan detail lengkap balita dengan grafik dan riwayat"""
    balita = get_object_or_404(Balita, id=id)
    today = date.today()
    
    # Hitung usia
    if balita.tanggal_lahir:
        usia_tahun = today.year - balita.tanggal_lahir.year
        usia_bulan = today.month - balita.tanggal_lahir.month
        usia_hari = today.day - balita.tanggal_lahir.day
        
        if usia_hari < 0:
            usia_bulan -= 1
            last_month = today.replace(day=1) - timedelta(days=1)
            usia_hari += last_month.day
        
        if usia_bulan < 0:
            usia_tahun -= 1
            usia_bulan += 12
        
        usia_display = f"{usia_tahun} tahun {usia_bulan} bulan {usia_hari} hari"
        if usia_tahun == 0:
            usia_display = f"{usia_bulan} bulan {usia_hari} hari"
        if usia_bulan == 0 and usia_tahun == 0:
            usia_display = f"{usia_hari} hari"
    else:
        usia_display = "-"
        usia_tahun = 0
        usia_bulan = 0
        usia_hari = 0
    
    # Ambil data penimbangan
    riwayat_penimbangan = Penimbangan.objects.filter(balita=balita).order_by('-tanggal')
    
    # Data untuk grafik (12 data terakhir - urutan ascending)
    chart_penimbangan = riwayat_penimbangan.order_by('tanggal')[:12]
    chart_labels = [p.tanggal.strftime('%b %Y') for p in chart_penimbangan]
    chart_berat = [float(p.berat_badan) for p in chart_penimbangan] if chart_penimbangan else []
    chart_tinggi = [float(p.tinggi_badan) for p in chart_penimbangan] if chart_penimbangan else []
    
    # Penimbangan terakhir
    penimbangan_terakhir = riwayat_penimbangan.first()
    
    # Ambil data imunisasi
    riwayat_imunisasi = Imunisasi.objects.filter(balita=balita).order_by('-tanggal')
    
    # Statistik - hitung rata-rata dengan aman
    total_penimbangan = riwayat_penimbangan.count()
    
    if total_penimbangan > 0:
        rata_rata_berat = riwayat_penimbangan.aggregate(avg_berat=Avg('berat_badan'))['avg_berat'] or 0
        rata_rata_tinggi = riwayat_penimbangan.aggregate(avg_tinggi=Avg('tinggi_badan'))['avg_tinggi'] or 0
        rata_rata_berat = round(float(rata_rata_berat), 2)
        rata_rata_tinggi = round(float(rata_rata_tinggi), 2)
    else:
        rata_rata_berat = 0
        rata_rata_tinggi = 0
    
    # Hitung persentase kelengkapan imunisasi
    total_imunisasi = riwayat_imunisasi.count()
    imunisasi_sudah = riwayat_imunisasi.filter(status='Sudah').count()
    persen_imunisasi = round((imunisasi_sudah / total_imunisasi * 100) if total_imunisasi > 0 else 0)
    
    # Imunisasi berikutnya (yang belum)
    imunisasi_berikutnya = riwayat_imunisasi.filter(status='Belum').first()
    
    context = {
        'balita': balita,
        'usia_display': usia_display,
        'usia_tahun': usia_tahun,
        'usia_bulan': usia_bulan,
        'usia_hari': usia_hari,
        'riwayat_penimbangan': riwayat_penimbangan[:10],
        'riwayat_imunisasi': riwayat_imunisasi[:10],
        'penimbangan_terakhir': penimbangan_terakhir,
        'chart_labels': chart_labels,
        'chart_berat': chart_berat,
        'chart_tinggi': chart_tinggi,
        'total_penimbangan': total_penimbangan,
        'rata_rata_berat': rata_rata_berat,
        'rata_rata_tinggi': rata_rata_tinggi,
        'total_imunisasi': total_imunisasi,
        'imunisasi_sudah': imunisasi_sudah,
        'persen_imunisasi': persen_imunisasi,
        'imunisasi_berikutnya': imunisasi_berikutnya,
    }
    return render(request, 'balita/detail.html', context)


@login_required
def balita_hubungkan_user(request, id):
    """Menghubungkan balita dengan user orang tua"""
    if not request.user.is_staff and not request.user.is_superuser:
        messages.error(request, 'Akses ditolak!')
        return redirect('balita:balita_list')
    
    balita = get_object_or_404(Balita, id=id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = get_object_or_404(User, id=user_id)
        
        # Pastikan user memiliki group Orang Tua
        group_ortu, _ = Group.objects.get_or_create(name='Orang Tua')
        if not user.groups.filter(name='Orang Tua').exists():
            user.groups.add(group_ortu)
        
        balita.user = user
        balita.save()
        
        messages.success(request, f'Berhasil menghubungkan balita {balita.nama} dengan user {user.username}')
        return redirect('balita:balita_detail', id=balita.id)
    
    # Ambil semua user dengan group Orang Tua
    users = User.objects.filter(groups__name='Orang Tua').order_by('username')
    
    context = {
        'balita': balita,
        'users': users,
    }
    return render(request, 'balita/hubungkan_user.html', context)