from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q  # Tambahkan import Q
from .models import Artikel
from datetime import datetime


@login_required
def artikel_list(request):
    """Menampilkan daftar artikel"""
    user = request.user
    
    # Jika admin atau staff, bisa lihat semua artikel (termasuk draft)
    if user.is_staff:
        artikel_list = Artikel.objects.all().order_by('-published_at')
    else:
        # Kader hanya bisa lihat artikel published milik sendiri + semua artikel published
        artikel_list = Artikel.objects.filter(
            Q(status='published') | 
            Q(penulis=user.get_full_name()) |
            Q(penulis=user.username)
        ).order_by('-published_at')
    
    # Filter by kategori
    kategori = request.GET.get('kategori')
    if kategori:
        artikel_list = artikel_list.filter(kategori=kategori)
    
    # Filter by status (untuk admin/kader)
    status = request.GET.get('status')
    if status and (user.is_staff or user.groups.filter(name='Kader').exists()):
        artikel_list = artikel_list.filter(status=status)
    
    # Pagination
    paginator = Paginator(artikel_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = Artikel.KATEGORI_CHOICES
    
    context = {
        'artikel_list': page_obj,
        'categories': categories,
        'selected_kategori': kategori,
        'selected_status': status,
        'is_staff': user.is_staff,
    }
    return render(request, 'artikel/list.html', context)


@login_required
def artikel_detail(request, id):
    """Menampilkan detail artikel"""
    artikel = get_object_or_404(Artikel, id=id)
    
    # Cek apakah user bisa melihat artikel draft
    user = request.user
    if artikel.status == 'draft':
        if not (user.is_staff or user.groups.filter(name='Kader').exists() or 
                artikel.penulis == user.get_full_name() or artikel.penulis == user.username):
            messages.error(request, 'Anda tidak memiliki akses untuk melihat artikel ini!')
            return redirect('artikel:artikel_list')
    
    # Increase view count
    artikel.increase_views()
    
    # Get related articles (same category)
    artikel_terkait = Artikel.objects.filter(
        kategori=artikel.kategori, 
        status='published'
    ).exclude(id=artikel.id)[:3]
    
    context = {
        'artikel': artikel,
        'artikel_terkait': artikel_terkait,
    }
    return render(request, 'artikel/detail.html', context)


@login_required
def artikel_create(request):
    """Form untuk menambah artikel baru"""
    if request.method == 'POST':
        try:
            judul = request.POST.get('judul')
            kategori = request.POST.get('kategori')
            konten = request.POST.get('konten')
            ringkasan = request.POST.get('ringkasan', '')
            tags = request.POST.get('tags', '')
            status = request.POST.get('status', 'published')
            
            if not judul or not kategori or not konten:
                messages.error(request, 'Mohon isi field yang wajib diisi!')
                return render(request, 'artikel/form.html', {'categories': Artikel.KATEGORI_CHOICES})
            
            artikel = Artikel.objects.create(
                judul=judul,
                kategori=kategori,
                konten=konten,
                ringkasan=ringkasan if ringkasan else konten[:200],
                tags=tags,
                status=status,
                penulis=request.user.get_full_name() or request.user.username
            )
            
            messages.success(request, f'Artikel "{artikel.judul}" berhasil ditambahkan!')
            return redirect('artikel:artikel_detail', id=artikel.id)
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'artikel/form.html', {'categories': Artikel.KATEGORI_CHOICES})


@login_required
def artikel_edit(request, id):
    """Form untuk mengedit artikel"""
    artikel = get_object_or_404(Artikel, id=id)
    user = request.user
    
    # Cek apakah user berhak mengedit (pemilik artikel atau staff)
    if not (user.is_staff or artikel.penulis == user.get_full_name() or artikel.penulis == user.username):
        messages.error(request, 'Anda tidak memiliki akses untuk mengedit artikel ini!')
        return redirect('artikel:artikel_list')
    
    if request.method == 'POST':
        try:
            artikel.judul = request.POST.get('judul')
            artikel.kategori = request.POST.get('kategori')
            artikel.konten = request.POST.get('konten')
            artikel.ringkasan = request.POST.get('ringkasan', '')
            artikel.tags = request.POST.get('tags', '')
            artikel.status = request.POST.get('status', 'published')
            
            if not artikel.ringkasan:
                artikel.ringkasan = artikel.konten[:200]
            
            artikel.save()
            
            messages.success(request, f'Artikel "{artikel.judul}" berhasil diupdate!')
            return redirect('artikel:artikel_detail', id=artikel.id)
            
        except Exception as e:
            messages.error(request, f'Terjadi kesalahan: {str(e)}')
    
    return render(request, 'artikel/form.html', {
        'artikel': artikel,
        'categories': Artikel.KATEGORI_CHOICES
    })


@login_required
def artikel_delete(request, id):
    """Menghapus artikel"""
    artikel = get_object_or_404(Artikel, id=id)
    user = request.user
    
    # Cek apakah user berhak menghapus (pemilik artikel atau staff)
    if not (user.is_staff or artikel.penulis == user.get_full_name() or artikel.penulis == user.username):
        messages.error(request, 'Anda tidak memiliki akses untuk menghapus artikel ini!')
        return redirect('artikel:artikel_list')
    
    if request.method == 'POST':
        judul = artikel.judul
        artikel.delete()
        messages.success(request, f'Artikel "{judul}" berhasil dihapus!')
        return redirect('artikel:artikel_list')
    
    return render(request, 'artikel/confirm_delete.html', {'artikel': artikel})