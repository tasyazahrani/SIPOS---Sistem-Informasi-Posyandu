from django import forms
from .models import Balita

class BalitaForm(forms.ModelForm):
    class Meta:
        model = Balita
        fields = [
            'nama', 'nik', 'jenis_kelamin', 'tempat_lahir', 
            'tanggal_lahir', 'berat_lahir', 'tinggi_lahir',
            'nama_ibu', 'nama_ayah', 'alamat'
        ]
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Masukkan nama lengkap balita'
            }),
            'nik': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': '16 digit NIK',
                'maxlength': '16'
            }),
            'jenis_kelamin': forms.Select(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none appearance-none bg-white'
            }),
            'tempat_lahir': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Contoh: Jakarta'
            }),
            'tanggal_lahir': forms.DateInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'type': 'date'
            }),
            'berat_lahir': forms.NumberInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Contoh: 3.2',
                'step': '0.01'
            }),
            'tinggi_lahir': forms.NumberInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Contoh: 48.5',
                'step': '0.01'
            }),
            'nama_ibu': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Nama lengkap ibu'
            }),
            'nama_ayah': forms.TextInput(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Nama lengkap ayah'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-xl focus:ring-2 focus:ring-[#2b6e3c] focus:border-[#2b6e3c] outline-none transition-all',
                'placeholder': 'Alamat lengkap balita',
                'rows': 3
            }),
        }
        labels = {
            'nama': 'Nama Lengkap Balita',
            'nik': 'NIK (Nomor Induk Kependudukan)',
            'jenis_kelamin': 'Jenis Kelamin',
            'tempat_lahir': 'Tempat Lahir',
            'tanggal_lahir': 'Tanggal Lahir',
            'berat_lahir': 'Berat Badan Lahir (kg)',
            'tinggi_lahir': 'Tinggi Badan Lahir (cm)',
            'nama_ibu': 'Nama Ibu Kandung',
            'nama_ayah': 'Nama Ayah Kandung',
            'alamat': 'Alamat',
        }