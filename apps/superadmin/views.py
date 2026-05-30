from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.core.paginator import Paginator
from django.db.models import Q
from apps.balita.models import Balita
from datetime import datetime, timedelta
from calendar import month_name


def superadmin_required(view_func):
    """Decorator untuk memastikan user adalah super admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_superuser:
            messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@superadmin_required
def dashboard(request):
    """Super Admin Dashboard"""
    # Statistik
    total_users = User.objects.count()
    total_kader = User.objects.filter(groups__name='Kader').count()
    total_ortu = User.objects.filter(groups__name='Orang Tua').count()
    total_balita = Balita.objects.count()
    total_posyandu = 5
    
    # User baru bulan ini
    today = datetime.now().date()
    first_day_month = today.replace(day=1)
    user_baru = User.objects.filter(date_joined__date__gte=first_day_month).count()
    
    # Data untuk chart
    chart_labels = []
    chart_data = []
    for i in range(5, -1, -1):
        month = today.replace(day=1) - timedelta(days=30 * i)
        month_start = month.replace(day=1)
        if month.month == 12:
            month_end = month.replace(year=month.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = month.replace(month=month.month + 1, day=1) - timedelta(days=1)
        
        chart_labels.append(month_name[month.month][:3])
        count = User.objects.filter(date_joined__date__gte=month_start, date_joined__date__lte=month_end).count()
        chart_data.append(count)
    
    # User terbaru
    user_terbaru = User.objects.all().order_by('-date_joined')[:5]
    
    # Balita terbaru
    balita_terbaru = Balita.objects.all().order_by('-created_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_kader': total_kader,
        'total_ortu': total_ortu,
        'total_balita': total_balita,
        'total_posyandu': total_posyandu,
        'user_baru': user_baru,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'user_terbaru': user_terbaru,
        'balita_terbaru': balita_terbaru,
    }
    return render(request, 'superadmin/dashboard.html', context)


# ==================== MANAJEMEN KADER ====================

@login_required
@superadmin_required
def manajemen_kader(request):
    """Halaman manajemen kader"""
    kader = User.objects.filter(groups__name='Kader').order_by('-date_joined')
    
    # Search
    search = request.GET.get('search')
    if search:
        kader = kader.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(kader, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'kader': page_obj,
        'search': search,
    }
    return render(request, 'superadmin/manajemen_kader.html', context)


@login_required
@superadmin_required
def kader_create(request):
    """Tambah kader baru"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        posyandu = request.POST.get('posyandu', '')
        
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
            return render(request, 'superadmin/kader_form.html')
        
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )
        
        # Tambahkan ke group Kader
        group_kader, _ = Group.objects.get_or_create(name='Kader')
        user.groups.add(group_kader)
        
        messages.success(request, f'Kader "{username}" berhasil ditambahkan!')
        return redirect('superadmin:manajemen_kader')
    
    return render(request, 'superadmin/kader_form.html')


@login_required
@superadmin_required
def kader_edit(request, id):
    """Edit kader"""
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        is_active = request.POST.get('is_active') == 'on'
        
        kader.email = email
        kader.first_name = first_name
        kader.is_active = is_active
        kader.save()
        
        messages.success(request, f'Data kader "{kader.username}" berhasil diupdate!')
        return redirect('superadmin:manajemen_kader')
    
    return render(request, 'superadmin/kader_form.html', {'kader': kader})


@login_required
@superadmin_required
def kader_delete(request, id):
    """Hapus kader"""
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    # Cegah menghapus diri sendiri jika dia juga super admin
    if kader.id == request.user.id and request.user.is_superuser:
        messages.error(request, 'Anda tidak dapat menghapus akun sendiri!')
        return redirect('superadmin:manajemen_kader')
    
    if request.method == 'POST':
        username = kader.username
        kader.delete()
        messages.success(request, f'Kader "{username}" berhasil dihapus!')
        return redirect('superadmin:manajemen_kader')
    
    return render(request, 'superadmin/kader_confirm_delete.html', {'kader': kader})


@login_required
@superadmin_required
def kader_reset_password(request, id):
    """Reset password kader"""
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
            return redirect('superadmin:manajemen_kader')
    
    return render(request, 'superadmin/kader_reset_password.html', {'kader': kader})


@login_required
@superadmin_required
def kader_detail(request, id):
    """Detail kader"""
    kader = get_object_or_404(User, id=id, groups__name='Kader')
    
    # Ambil statistik aktivitas kader
    total_balita_input = Balita.objects.filter(created_by=kader).count() if hasattr(Balita, 'created_by') else 0
    
    context = {
        'kader': kader,
        'total_balita_input': total_balita_input,
    }
    return render(request, 'superadmin/kader_detail.html', context)


# ==================== MANAJEMEN USER ====================

@login_required
@superadmin_required
def manajemen_user(request):
    """Halaman manajemen user"""
    users = User.objects.exclude(is_superuser=True).order_by('-date_joined')
    
    # Search
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(email__icontains=search)
        )
    
    # Filter role
    role = request.GET.get('role')
    if role == 'kader':
        users = users.filter(groups__name='Kader')
    elif role == 'ortu':
        users = users.filter(groups__name='Orang Tua')
    elif role == 'admin':
        users = users.filter(is_staff=True)
    
    # Pagination
    paginator = Paginator(users, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'search': search,
        'role_filter': role,
    }
    return render(request, 'superadmin/manajemen_user.html', context)


@login_required
@superadmin_required
def user_create(request):
    """Tambah user baru"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        errors = []
        if not username:
            errors.append('Username harus diisi!')
        elif User.objects.filter(username=username).exists():
            errors.append('Username sudah digunakan!')
        
        if email and User.objects.filter(email=email).exists():
            errors.append('Email sudah terdaftar!')
        
        if not password:
            errors.append('Password harus diisi!')
        elif len(password) < 8:
            errors.append('Password minimal 8 karakter!')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'superadmin/user_form.html')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )
        
        if role == 'kader':
            group, _ = Group.objects.get_or_create(name='Kader')
            user.groups.add(group)
        elif role == 'ortu':
            group, _ = Group.objects.get_or_create(name='Orang Tua')
            user.groups.add(group)
        elif role == 'admin':
            user.is_staff = True
            user.save()
        
        messages.success(request, f'User "{username}" berhasil ditambahkan!')
        return redirect('superadmin:manajemen_user')
    
    return render(request, 'superadmin/user_form.html')


@login_required
@superadmin_required
def user_edit(request, id):
    """Edit user"""
    user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        user.email = email
        user.first_name = first_name
        user.is_active = is_active
        user.save()
        
        user.groups.clear()
        
        if role == 'kader':
            group, _ = Group.objects.get_or_create(name='Kader')
            user.groups.add(group)
            user.is_staff = False
        elif role == 'ortu':
            group, _ = Group.objects.get_or_create(name='Orang Tua')
            user.groups.add(group)
            user.is_staff = False
        elif role == 'admin':
            user.is_staff = True
        user.save()
        
        messages.success(request, f'User "{user.username}" berhasil diupdate!')
        return redirect('superadmin:manajemen_user')
    
    current_role = 'ortu'
    if user.is_superuser:
        current_role = 'superadmin'
    elif user.is_staff:
        current_role = 'admin'
    elif user.groups.filter(name='Kader').exists():
        current_role = 'kader'
    
    return render(request, 'superadmin/user_form.html', {'user': user, 'current_role': current_role})


@login_required
@superadmin_required
def user_delete(request, id):
    """Hapus user"""
    user = get_object_or_404(User, id=id)
    
    if user.id == request.user.id:
        messages.error(request, 'Anda tidak dapat menghapus akun sendiri!')
        return redirect('superadmin:manajemen_user')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" berhasil dihapus!')
        return redirect('superadmin:manajemen_user')
    
    return render(request, 'superadmin/user_confirm_delete.html', {'user': user})


@login_required
@superadmin_required
def user_reset_password(request, id):
    """Reset password user"""
    user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        
        if not new_password:
            messages.error(request, 'Password baru harus diisi!')
        elif len(new_password) < 8:
            messages.error(request, 'Password minimal 8 karakter!')
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, f'Password untuk "{user.username}" berhasil direset!')
            return redirect('superadmin:manajemen_user')
    
    return render(request, 'superadmin/user_reset_password.html', {'user': user})


# ==================== FUNGSI LAINNYA ====================

@login_required
@superadmin_required
def manajemen_posyandu(request):
    """Halaman manajemen posyandu"""
    return render(request, 'superadmin/manajemen_posyandu.html')


@login_required
@superadmin_required
def laporan_sistem(request):
    """Halaman laporan sistem"""
    return render(request, 'superadmin/laporan_sistem.html')


@login_required
@superadmin_required
def backup_data(request):
    """Halaman backup data"""
    return render(request, 'superadmin/backup_data.html')


@login_required
@superadmin_required
def pengaturan_sistem(request):
    """Halaman pengaturan sistem"""
    return render(request, 'superadmin/pengaturan_sistem.html')


@login_required
@superadmin_required
def pengaturan(request):
    """Halaman pengaturan akun super admin"""
    if request.method == 'POST':
        user = request.user
        first_name = request.POST.get('first_name')
        email = request.POST.get('email')
        
        if first_name:
            user.first_name = first_name
        if email:
            user.email = email
        user.save()
        
        messages.success(request, 'Pengaturan berhasil disimpan!')
        return redirect('superadmin:pengaturan')
    
    return render(request, 'superadmin/pengaturan.html', {'user': request.user})