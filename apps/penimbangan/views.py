from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Penimbangan
from apps.balita.models import Balita
from datetime import date, datetime
from django.db import models


def hitung_status_gizi(berat_badan, tinggi_badan, tanggal_lahir, tanggal_penimbangan):
    """
    Menghitung status gizi berdasarkan standar WHO
    Menggunakan indeks BB/U (Berat Badan berdasarkan Umur)
    """
    if not berat_badan or not tinggi_badan or not tanggal_lahir:
        return 'Normal'
    
    # Konversi ke date object jika masih string
    if isinstance(tanggal_penimbangan, str):
        tanggal_penimbangan = datetime.strptime(tanggal_penimbangan, '%Y-%m-%d').date()
    
    if isinstance(tanggal_lahir, str):
        tanggal_lahir = datetime.strptime(tanggal_lahir, '%Y-%m-%d').date()
    
    # Hitung usia dalam bulan
    age_months = (tanggal_penimbangan.year - tanggal_lahir.year) * 12 + (tanggal_penimbangan.month - tanggal_lahir.month)
    if tanggal_penimbangan.day < tanggal_lahir.day:
        age_months -= 1
    
    # Jika usia negatif atau 0, anggap normal
    if age_months <= 0:
        return 'Normal'
    
    berat = float(berat_badan)
    
    # Standar berat badan ideal berdasarkan usia (sederhana)
    if age_months <= 6:
        berat_ideal_min = 3.5 + (age_months * 0.7)
    elif age_months <= 12:
        usia_sisa = age_months - 6
        berat_ideal_min = 7.5 + (usia_sisa * 0.5)
    elif age_months <= 24:
        usia_sisa = age_months - 12
        berat_ideal_min = 9.5 + (usia_sisa * 0.3)
    else:
        usia_sisa = age_months - 24
        berat_ideal_min = 12.5 + (usia_sisa * 0.2)
    
    # Hitung persentase dari standar
    if berat_ideal_min > 0:
        persentase = (berat / berat_ideal_min) * 100
    else:
        persentase = 100
    
    if persentase < 60:
        return 'Gizi Buruk'
    elif persentase < 80:
        return 'Gizi Kurang'
    elif persentase > 120:
        return 'Gizi Lebih'
    else:
        return 'Normal'


@login_required
def penimbangan_list(request):
    """Menampilkan daftar penimbangan"""
    penimbangan_list = Penimbangan.objects.select_related('balita').all().order_by('-tanggal')
    return render(request, 'penimbangan/list.html', {'penimbangan_list': penimbangan_list})


@login_required
def penimbangan_create(request):
    """Form untuk menambah data penimbangan"""
    if request.method == 'POST':
        try:
            balita_id = request.POST.get('balita')
            tanggal_str = request.POST.get('tanggal')
            berat_badan = request.POST.get('berat_badan')
            tinggi_badan = request.POST.get('tinggi_badan')
            status_gizi = request.POST.get('status_gizi', '')
            keterangan = request.POST.get('keterangan', '')
            
            # Validasi
            if not balita_id:
                messages.error(request, 'Pilih balita terlebih dahulu!')
                return render(request, 'penimbangan/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not tanggal_str:
                messages.error(request, 'Tanggal penimbangan harus diisi!')
                return render(request, 'penimbangan/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not berat_badan:
                messages.error(request, 'Berat badan harus diisi!')
                return render(request, 'penimbangan/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not tinggi_badan:
                messages.error(request, 'Tinggi badan harus diisi!')
                return render(request, 'penimbangan/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            # Konversi ke tipe data yang benar
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            berat = float(berat_badan)
            tinggi = float(tinggi_badan)
            
            balita = Balita.objects.get(id=balita_id)
            
            # Buat objek penimbangan
            penimbangan = Penimbangan(
                balita=balita,
                tanggal=tanggal,
                berat_badan=berat,
                tinggi_badan=tinggi,
                keterangan=keterangan
            )
            
            # Set status gizi jika diisi manual
            if status_gizi:
                penimbangan.status_gizi = status_gizi
            
            penimbangan.save()  # Auto hitung status gizi
            
            messages.success(request, 'Data penimbangan berhasil ditambahkan!')
            return redirect('penimbangan:penimbangan_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    balita_list = Balita.objects.all().order_by('nama')
    return render(request, 'penimbangan/form.html', {
        'balita_list': balita_list,
        'today': date.today()
    })


@login_required
def penimbangan_edit(request, id):
    """Form untuk mengedit data penimbangan"""
    penimbangan = get_object_or_404(Penimbangan, id=id)
    
    if request.method == 'POST':
        try:
            balita_id = request.POST.get('balita')
            tanggal_str = request.POST.get('tanggal')
            berat_badan = request.POST.get('berat_badan')
            tinggi_badan = request.POST.get('tinggi_badan')
            status_gizi = request.POST.get('status_gizi')
            keterangan = request.POST.get('keterangan', '')
            
            # Validasi
            if not balita_id:
                messages.error(request, 'Pilih balita terlebih dahulu!')
                return render(request, 'penimbangan/form.html', {
                    'penimbangan': penimbangan,
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not berat_badan:
                messages.error(request, 'Berat badan harus diisi!')
                return render(request, 'penimbangan/form.html', {
                    'penimbangan': penimbangan,
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            # Konversi tanggal string ke date object
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            penimbangan.balita_id = balita_id
            penimbangan.tanggal = tanggal
            penimbangan.berat_badan = berat_badan
            penimbangan.tinggi_badan = tinggi_badan
            penimbangan.status_gizi = status_gizi
            penimbangan.keterangan = keterangan
            penimbangan.save()
            
            messages.success(request, 'Data penimbangan berhasil diupdate!')
            return redirect('penimbangan:penimbangan_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    balita_list = Balita.objects.all().order_by('nama')
    return render(request, 'penimbangan/form.html', {
        'penimbangan': penimbangan,
        'balita_list': balita_list,
        'today': date.today()
    })


@login_required
def penimbangan_delete(request, id):
    """Menghapus data penimbangan"""
    penimbangan = get_object_or_404(Penimbangan, id=id)
    
    if request.method == 'POST':
        nama_balita = penimbangan.balita.nama
        penimbangan.delete()
        messages.success(request, f'Data penimbangan {nama_balita} berhasil dihapus!')
        return redirect('penimbangan:penimbangan_list')
    
    return render(request, 'penimbangan/confirm_delete.html', {'penimbangan': penimbangan})