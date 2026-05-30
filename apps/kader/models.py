from django.contrib.auth.models import User
from django.db import models


class KaderProfile(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='kaderprofile',
        verbose_name='Pengguna'
    )
    no_hp = models.CharField(max_length=15, verbose_name='No. Handphone')
    alamat = models.TextField(verbose_name='Alamat')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil {self.user.username}"

    class Meta:
        verbose_name = 'Profil Kader'
        verbose_name_plural = 'Profil Kader'