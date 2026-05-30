from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.db.models import Q


@login_required
def kader_list(request):
    """Menampilkan daftar semua kader"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    # Ambil semua user yang memiliki group Kader
    kader_list = User.objects.filter(groups__name='Kader').order_by('-date_joined')
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        kader_list = kader_list.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(kader_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'kader_list': page_obj,
        'search': search,
    }
    return render(request, 'kader/list.html', context)


@login_required
def kader_create(request):
    """Form untuk menambah kader baru"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        
        # Validasi
        errors = []
        if not username:
            errors.append('Username harus diisi!')
        elif User.objects.filter(username=username).exists():
            errors.append('Username sudah digunakan!')
        
        if email and User.objects.filter(email=email).exists():
            errors.append('Email sudah terdaftar!')
        
        if not first_name:
            errors.append('Nama lengkap harus diisi!')
        
        if not password:
            errors.append('Password harus diisi!')
        elif len(password) < 8:
            errors.append('Password minimal 8 karakter!')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'kader/form.html')
        
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            is_staff=False,
            is_superuser=False
        )
        
        # Tambahkan ke group Kader
        group_kader, _ = Group.objects.get_or_create(name='Kader')
        user.groups.add(group_kader)
        
        messages.success(request, f'Kader "{username}" berhasil ditambahkan!')
        return redirect('kader:kader_list')
    
    return render(request, 'kader/form.html')


@login_required
def kader_edit(request, id):
    """Form untuk mengedit kader"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        
        if first_name:
            kader.first_name = first_name
        if email:
            kader.email = email
        
        kader.save()
        
        messages.success(request, f'Data kader "{kader.username}" berhasil diupdate!')
        return redirect('kader:kader_list')
    
    return render(request, 'kader/form.html', {'kader': kader})


@login_required
def kader_delete(request, id):
    """Menghapus kader"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    # Cegah menghapus diri sendiri
    if kader.id == request.user.id:
        messages.error(request, 'Anda tidak dapat menghapus akun sendiri!')
        return redirect('kader:kader_list')
    
    if request.method == 'POST':
        username = kader.username
        kader.delete()
        messages.success(request, f'Kader "{username}" berhasil dihapus!')
        return redirect('kader:kader_list')
    
    return render(request, 'kader/confirm_delete.html', {'kader': kader})


@login_required
def kader_reset_password(request, id):
    """Reset password kader"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not new_password:
            messages.error(request, 'Password baru harus diisi!')
        elif len(new_password) < 8:
            messages.error(request, 'Password minimal 8 karakter!')
        elif new_password != confirm_password:
            messages.error(request, 'Konfirmasi password tidak sama!')
        else:
            kader.set_password(new_password)
            kader.save()
            messages.success(request, f'Password untuk "{kader.username}" berhasil direset!')
            return redirect('kader:kader_list')
    
    return render(request, 'kader/reset_password.html', {'kader': kader})


@login_required
def kader_detail(request, id):
    """Menampilkan detail kader"""
    # Hanya super admin dan admin yang bisa akses
    if not request.user.is_superuser and not request.user.is_staff:
        messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
        return redirect('dashboard')
    
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    context = {
        'kader': kader,
    }
    return render(request, 'kader/detail.html', context)