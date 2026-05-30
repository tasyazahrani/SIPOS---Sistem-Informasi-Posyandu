from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Imunisasi
from apps.balita.models import Balita
from datetime import date, datetime


@login_required
def imunisasi_list(request):
    """Menampilkan daftar imunisasi"""
    imunisasi_list = Imunisasi.objects.select_related('balita').all().order_by('-tanggal')
    return render(request, 'imunisasi/list.html', {'imunisasi_list': imunisasi_list})


@login_required
def imunisasi_create(request):
    """Form untuk menambah data imunisasi"""
    if request.method == 'POST':
        try:
            balita_id = request.POST.get('balita')
            jenis_imunisasi = request.POST.get('jenis_imunisasi')
            tanggal_str = request.POST.get('tanggal')
            status = request.POST.get('status')
            tempat = request.POST.get('tempat', '')
            keterangan = request.POST.get('keterangan', '')
            
            # Validasi
            if not balita_id:
                messages.error(request, 'Pilih balita terlebih dahulu!')
                return render(request, 'imunisasi/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not jenis_imunisasi:
                messages.error(request, 'Pilih jenis imunisasi!')
                return render(request, 'imunisasi/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            if not tanggal_str:
                messages.error(request, 'Tanggal imunisasi harus diisi!')
                return render(request, 'imunisasi/form.html', {
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            Imunisasi.objects.create(
                balita_id=balita_id,
                jenis_imunisasi=jenis_imunisasi,
                tanggal=tanggal,
                status=status,
                tempat=tempat,
                keterangan=keterangan
            )
            messages.success(request, 'Data imunisasi berhasil ditambahkan!')
            return redirect('imunisasi:imunisasi_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    balita_list = Balita.objects.all().order_by('nama')
    return render(request, 'imunisasi/form.html', {
        'balita_list': balita_list,
        'today': date.today()
    })


@login_required
def imunisasi_edit(request, id):
    """Form untuk mengedit data imunisasi"""
    imunisasi = get_object_or_404(Imunisasi, id=id)
    
    if request.method == 'POST':
        try:
            balita_id = request.POST.get('balita')
            jenis_imunisasi = request.POST.get('jenis_imunisasi')
            tanggal_str = request.POST.get('tanggal')
            status = request.POST.get('status')
            tempat = request.POST.get('tempat', '')
            keterangan = request.POST.get('keterangan', '')
            
            if not balita_id:
                messages.error(request, 'Pilih balita terlebih dahulu!')
                return render(request, 'imunisasi/form.html', {
                    'imunisasi': imunisasi,
                    'balita_list': Balita.objects.all().order_by('nama'),
                    'today': date.today()
                })
            
            tanggal = datetime.strptime(tanggal_str, '%Y-%m-%d').date()
            
            imunisasi.balita_id = balita_id
            imunisasi.jenis_imunisasi = jenis_imunisasi
            imunisasi.tanggal = tanggal
            imunisasi.status = status
            imunisasi.tempat = tempat
            imunisasi.keterangan = keterangan
            imunisasi.save()
            
            messages.success(request, 'Data imunisasi berhasil diupdate!')
            return redirect('imunisasi:imunisasi_list')
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    balita_list = Balita.objects.all().order_by('nama')
    return render(request, 'imunisasi/form.html', {
        'imunisasi': imunisasi,
        'balita_list': balita_list,
        'today': date.today()
    })


@login_required
def imunisasi_delete(request, id):
    """Menghapus data imunisasi"""
    imunisasi = get_object_or_404(Imunisasi, id=id)
    
    if request.method == 'POST':
        nama_balita = imunisasi.balita.nama
        imunisasi.delete()
        messages.success(request, f'Data imunisasi {nama_balita} berhasil dihapus!')
        return redirect('imunisasi:imunisasi_list')
    
    return render(request, 'imunisasi/confirm_delete.html', {'imunisasi': imunisasi})