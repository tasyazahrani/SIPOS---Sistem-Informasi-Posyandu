from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Jadwal
from datetime import datetime, date


@login_required
def jadwal_list(request):
    """Menampilkan daftar jadwal posyandu"""
    jadwal_list = Jadwal.objects.all().order_by('tanggal', 'waktu_mulai')
    return render(request, 'jadwal/list.html', {'jadwal_list': jadwal_list})


@login_required
def jadwal_create(request):
    """Form untuk menambah jadwal posyandu"""
    if request.method == 'POST':
        try:
            nama_kegiatan = request.POST.get('nama_kegiatan')
            jenis_kegiatan = request.POST.get('jenis_kegiatan')
            tanggal_str = request.POST.get('tanggal')
            waktu_mulai = request.POST.get('waktu_mulai')
            waktu_selesai = request.POST.get('waktu_selesai')
            tempat = request.POST.get('tempat')
            petugas = request.POST.get('petugas', '')
            status = request.POST.get('status')
            keterangan = request.POST.get('keterangan', '')
            
            # Validasi
            if not nama_kegiatan:
                messages.error(request, 'Nama kegiatan harus diisi!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            if not jenis_kegiatan:
                messages.error(request, 'Pilih jenis kegiatan!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            if not tanggal_str:
                messages.error(request, 'Tanggal harus diisi!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            if not waktu_mulai:
                messages.error(request, 'Waktu mulai harus diisi!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            if not waktu_selesai:
                messages.error(request, 'Waktu selesai harus diisi!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            if not tempat:
                messages.error(request, 'Tempat harus diisi!')
                return render(request, 'jadwal/form.html', {'today': date.today()})
            
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            Jadwal.objects.create(
                nama_kegiatan=nama_kegiatan,
                jenis_kegiatan=jenis_kegiatan,
                tanggal=tanggal,
                waktu_mulai=waktu_mulai,
                waktu_selesai=waktu_selesai,
                tempat=tempat,
                petugas=petugas,
                status=status,
                keterangan=keterangan
            )
            messages.success(request, 'Jadwal posyandu berhasil ditambahkan!')
            return redirect('jadwal:jadwal_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'jadwal/form.html', {'today': date.today()})


@login_required
def jadwal_edit(request, id):
    """Form untuk mengedit jadwal posyandu"""
    jadwal = get_object_or_404(Jadwal, id=id)
    
    if request.method == 'POST':
        try:
            jadwal.nama_kegiatan = request.POST.get('nama_kegiatan')
            jadwal.jenis_kegiatan = request.POST.get('jenis_kegiatan')
            tanggal_str = request.POST.get('tanggal')
            jadwal.waktu_mulai = request.POST.get('waktu_mulai')
            jadwal.waktu_selesai = request.POST.get('waktu_selesai')
            jadwal.tempat = request.POST.get('tempat')
            jadwal.petugas = request.POST.get('petugas', '')
            jadwal.status = request.POST.get('status')
            jadwal.keterangan = request.POST.get('keterangan', '')
            jadwal.tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            jadwal.save()
            
            messages.success(request, 'Jadwal posyandu berhasil diupdate!')
            return redirect('jadwal:jadwal_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'jadwal/form.html', {'jadwal': jadwal, 'today': date.today()})


@login_required
def jadwal_delete(request, id):
    """Menghapus jadwal posyandu"""
    jadwal = get_object_or_404(Jadwal, id=id)
    
    if request.method == 'POST':
        nama_kegiatan = jadwal.nama_kegiatan
        jadwal.delete()
        messages.success(request, f'Jadwal "{nama_kegiatan}" berhasil dihapus!')
        return redirect('jadwal:jadwal_list')
    
    return render(request, 'jadwal/confirm_delete.html', {'jadwal': jadwal})