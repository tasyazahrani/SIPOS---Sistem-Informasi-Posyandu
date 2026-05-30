from django.contrib.auth.models import User
from django.db import models


class KaderProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    no_hp = models.CharField(max_length=15)
    alamat = models.TextField()

    def __str__(self):
        return self.user.username