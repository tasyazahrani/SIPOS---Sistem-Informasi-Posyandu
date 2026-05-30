from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from apps.balita.models import Balita
from apps.penimbangan.models import Penimbangan
from datetime import datetime, timedelta
from django.db import models
from django.db.models import Q


# ==================== CUSTOM LOGIN VIEW ====================
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Setelah login berhasil, redirect berdasarkan role yang dipilih"""
        response = super().form_valid(form)
        user = self.request.user
        login_role = self.request.POST.get('login_role', 'ortu')
        
        # SUPER ADMIN - langsung ke dashboard superadmin
        if user.is_superuser:
            return redirect('superadmin:dashboard')
        
        # ADMIN (staff) - langsung ke dashboard superadmin juga
        if user.is_staff:
            return redirect('superadmin:dashboard')
        
        # Cek group user
        is_kader = user.groups.filter(name='Kader').exists()
        is_ortu = user.groups.filter(name='Orang Tua').exists()
        
        # Jika user tidak memiliki group sama sekali, beri default ke Orang Tua
        if not is_kader and not is_ortu:
            group_ortu, _ = Group.objects.get_or_create(name='Orang Tua')
            user.groups.add(group_ortu)
            is_ortu = True
        
        # Redirect berdasarkan role yang dipilih dan group user
        if login_role == 'kader':
            if is_kader:
                return redirect('dashboard')
            else:
                messages.error(self.request, 'Akun ini tidak terdaftar sebagai Kader. Silakan pilih "Orang Tua" atau registrasi ulang.')
                return redirect('login')
        else:  # orang tua
            if is_ortu:
                return redirect('dashboard_ortu')
            elif is_kader:
                messages.warning(self.request, 'Anda login sebagai Kader, diarahkan ke Dashboard Kader.')
                return redirect('dashboard')
            else:
                messages.error(self.request, 'Akun tidak dikenali. Silakan hubungi admin.')
                return redirect('login')
    
    def get_success_url(self):
        return reverse_lazy('dashboard')


# ==================== LOGOUT ====================
def custom_logout(request):
    """Custom logout function"""
    auth_logout(request)
    messages.success(request, 'Anda telah berhasil keluar dari sistem.')
    return redirect('home')


# ==================== HALAMAN UTAMA ====================
def home(request):
    return render(request, 'home.html')


# ==================== REGISTRASI ====================
def register(request):
    """Halaman registrasi dengan pilihan role (Orang Tua / Kader)"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        role = request.POST.get('role', 'orang_tua')
        posyandu_code = request.POST.get('posyandu_code', '')
        child_nik = request.POST.get('child_nik', '')
        child_no_hp = request.POST.get('child_no_hp', '')
        
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
        
        if password1 != password2:
            errors.append('Password tidak sama!')
        
        if len(password1) < 8:
            errors.append('Password minimal 8 karakter!')
        
        if role == 'kader' and not posyandu_code:
            errors.append('Kode Posyandu harus diisi untuk pendaftaran sebagai kader!')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'registration/register.html')
        
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            first_name=first_name,
            is_staff=False,
            is_superuser=False
        )
        
        # Assign user ke group berdasarkan role
        if role == 'kader':
            group, created = Group.objects.get_or_create(name='Kader')
            user.groups.add(group)
            messages.success(request, 'Registrasi sebagai Kader berhasil! Silakan login.')
        else:
            group, created = Group.objects.get_or_create(name='Orang Tua')
            user.groups.add(group)
            
            # HUBUNGKAN USER DENGAN BALITA YANG SUDAH ADA
            balita = None
            if child_nik:
                balita = Balita.objects.filter(nik=child_nik, user__isnull=True).first()
            if not balita and child_no_hp:
                balita = Balita.objects.filter(no_hp_orang_tua=child_no_hp, user__isnull=True).first()
            if not balita:
                balita = Balita.objects.filter(nama_ibu__icontains=first_name, user__isnull=True).first()
            
            if balita:
                balita.user = user
                balita.save()
                messages.success(request, f'Registrasi berhasil! Akun Anda terhubung dengan data balita {balita.nama}.')
            else:
                messages.success(request, 'Registrasi sebagai Orang Tua berhasil! Silakan login.')
        
        return redirect('login')
    
    return render(request, 'registration/register.html')


# ==================== DASHBOARD KADER ====================
@login_required
def dashboard(request):
    """Dashboard untuk Kader / Admin"""
    today = datetime.now().date()
    first_day_month = today.replace(day=1)
    
    total_balita = Balita.objects.count()
    total_penimbangan = Penimbangan.objects.count()
    penimbangan_bulan_ini = Penimbangan.objects.filter(tanggal__gte=first_day_month).count()
    
    # Hitung balita dengan status gizi normal
    gizi_normal = Penimbangan.objects.filter(
        Q(status_gizi__icontains='Normal') | Q(status_gizi__icontains='normal')
    ).values('balita').distinct().count()
    
    if total_balita > 0:
        persen_gizi_normal = round((gizi_normal / total_balita) * 100)
    else:
        persen_gizi_normal = 0
    
    # 5 penimbangan terbaru
    penimbangan_terbaru = Penimbangan.objects.select_related('balita').all().order_by('-tanggal')[:5]
    
    # Data untuk chart (7 hari terakhir)
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        chart_labels.append(date.strftime('%d/%m'))
        avg_weight = Penimbangan.objects.filter(tanggal=date).aggregate(
            avg=models.Avg('berat_badan')
        )['avg'] or 0
        chart_data.append(float(avg_weight))
    
    # Distribusi status gizi
    status_normal = Penimbangan.objects.filter(
        Q(status_gizi__icontains='Normal') | Q(status_gizi__icontains='normal')
    ).count()
    status_kurang = Penimbangan.objects.filter(
        Q(status_gizi__icontains='Kurang') | Q(status_gizi__icontains='kurang')
    ).count()
    status_buruk = Penimbangan.objects.filter(
        Q(status_gizi__icontains='Buruk') | Q(status_gizi__icontains='buruk')
    ).count()
    
    # Persentase pertumbuhan
    last_month = today.replace(day=1) - timedelta(days=1)
    last_month_first = last_month.replace(day=1)
    penimbangan_bulan_lalu = Penimbangan.objects.filter(
        tanggal__gte=last_month_first,
        tanggal__lt=first_day_month
    ).count()
    
    if penimbangan_bulan_lalu > 0:
        persen_pertumbuhan = round((penimbangan_bulan_ini - penimbangan_bulan_lalu) / penimbangan_bulan_lalu * 100)
    else:
        persen_pertumbuhan = penimbangan_bulan_ini if penimbangan_bulan_ini > 0 else 0
    
    # Kegiatan bulan ini (dari model Jadwal)
    kegiatan_bulan_ini = 0
    try:
        from apps.jadwal.models import Jadwal
        kegiatan_bulan_ini = Jadwal.objects.filter(
            tanggal__gte=first_day_month,
            tanggal__lte=today
        ).count()
    except ImportError:
        pass
    
    context = {
        'total_balita': total_balita,
        'total_penimbangan': total_penimbangan,
        'penimbangan_bulan_ini': penimbangan_bulan_ini,
        'gizi_normal': gizi_normal,
        'persen_gizi_normal': persen_gizi_normal,
        'penimbangan_terbaru': penimbangan_terbaru,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'status_normal': status_normal,
        'status_kurang': status_kurang,
        'status_buruk': status_buruk,
        'persen_pertumbuhan': persen_pertumbuhan,
        'kegiatan_bulan_ini': kegiatan_bulan_ini,
    }
    return render(request, 'dashboard.html', context)


# ==================== DASHBOARD ORANG TUA ====================
@login_required
def dashboard_ortu(request):
    """Dashboard khusus untuk Orang Tua"""
    from datetime import date
    from apps.artikel.models import Artikel
    from apps.imunisasi.models import Imunisasi
    
    # Ambil balita berdasarkan user yang login
    try:
        balita = request.user.balita
    except:
        balita = None
        messages.info(request, 'Data anak belum terhubung dengan akun Anda. Silakan hubungi admin posyandu.')
    
    if not balita:
        context = {
            'balita': None,
            'usia_anak': '-',
            'penimbangan_terakhir': None,
            'selisih_berat': 0,
            'riwayat_penimbangan': [],
            'imunisasi_berikutnya': None,
            'artikel_terbaru': Artikel.objects.filter(status='published').order_by('-published_at')[:3],
            'chart_labels': [],
            'weight_data': [],
            'height_data': [],
        }
        return render(request, 'dashboard_ortu.html', context)
    
    # Hitung usia
    today = date.today()
    if balita and balita.tanggal_lahir:
        usia = today.year - balita.tanggal_lahir.year
        if today.month < balita.tanggal_lahir.month or \
           (today.month == balita.tanggal_lahir.month and today.day < balita.tanggal_lahir.day):
            usia -= 1
        usia_anak = f"{usia} tahun"
    else:
        usia_anak = "-"
    
    # Penimbangan terakhir
    penimbangan_terakhir = Penimbangan.objects.filter(balita=balita).order_by('-tanggal').first()
    
    # Selisih berat
    selisih_berat = 0
    if penimbangan_terakhir:
        penimbangan_sebelumnya = Penimbangan.objects.filter(
            balita=balita, 
            tanggal__lt=penimbangan_terakhir.tanggal
        ).order_by('-tanggal').first()
        if penimbangan_sebelumnya:
            selisih_berat = round(penimbangan_terakhir.berat_badan - penimbangan_sebelumnya.berat_badan, 2)
    
    # Riwayat penimbangan (5 terbaru)
    riwayat_penimbangan = Penimbangan.objects.filter(balita=balita).order_by('-tanggal')[:5]
    
    # Data chart (urut dari yang terlama ke terbaru untuk grafik)
    chart_labels = []
    weight_data = []
    height_data = []
    chart_penimbangan = Penimbangan.objects.filter(balita=balita).order_by('tanggal')
    for p in chart_penimbangan:
        chart_labels.append(p.tanggal.strftime('%b %Y'))
        weight_data.append(float(p.berat_badan))
        height_data.append(float(p.tinggi_badan))
    
    # Imunisasi berikutnya
    imunisasi_berikutnya = Imunisasi.objects.filter(
        balita=balita, 
        tanggal__gte=today
    ).order_by('tanggal').first()
    
    # Artikel terbaru
    artikel_terbaru = Artikel.objects.filter(status='published').order_by('-published_at')[:3]
    
    context = {
        'balita': balita,
        'usia_anak': usia_anak,
        'penimbangan_terakhir': penimbangan_terakhir,
        'selisih_berat': selisih_berat,
        'riwayat_penimbangan': riwayat_penimbangan,
        'imunisasi_berikutnya': imunisasi_berikutnya,
        'artikel_terbaru': artikel_terbaru,
        'chart_labels': chart_labels,
        'weight_data': weight_data,
        'height_data': height_data,
    }
    return render(request, 'dashboard_ortu.html', context)


# ==================== PENGATURAN ====================
@login_required
def pengaturan(request):
    """Halaman pengaturan user"""
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action', 'profile')
        
        if action == 'profile':
            first_name = request.POST.get('first_name')
            email = request.POST.get('email')
            
            if first_name:
                user.first_name = first_name
            if email:
                user.email = email
            
            user.save()
            messages.success(request, 'Profil berhasil diperbarui!')
            return redirect('pengaturan')
        
        elif action == 'password':
            old_password = request.POST.get('old_password')
            new_password1 = request.POST.get('new_password1')
            new_password2 = request.POST.get('new_password2')
            
            if not user.check_password(old_password):
                messages.error(request, 'Password lama salah!')
                return redirect('pengaturan')
            
            if new_password1 != new_password2:
                messages.error(request, 'Password baru tidak cocok!')
                return redirect('pengaturan')
            
            if len(new_password1) < 8:
                messages.error(request, 'Password minimal 8 karakter!')
                return redirect('pengaturan')
            
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password berhasil diubah!')
            return redirect('pengaturan')
        
        elif action == 'notification':
            email_notif = request.POST.get('email_notif') == 'on'
            sms_notif = request.POST.get('sms_notif') == 'on'
            
            request.session['email_notif'] = email_notif
            request.session['sms_notif'] = sms_notif
            
            messages.success(request, 'Preferensi notifikasi berhasil diperbarui!')
            return redirect('pengaturan')
    
    email_notif = request.session.get('email_notif', True)
    sms_notif = request.session.get('sms_notif', False)
    
    user_role = 'Orang Tua'
    if user.is_superuser:
        user_role = 'Super Admin'
    elif user.is_staff:
        user_role = 'Admin'
    elif user.groups.filter(name='Kader').exists():
        user_role = 'Kader Posyandu'
    elif user.groups.filter(name='Orang Tua').exists():
        user_role = 'Orang Tua'
    
    context = {
        'user': user,
        'user_role': user_role,
        'email_notif': email_notif,
        'sms_notif': sms_notif,
    }
    return render(request, 'pengaturan.html', context)