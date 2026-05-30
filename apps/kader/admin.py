from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import KaderProfile


# Inline untuk KaderProfile
class KaderProfileInline(admin.StackedInline):
    model = KaderProfile
    can_delete = False
    verbose_name_plural = 'Profil Kader'


# Custom User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'get_no_hp', 'get_alamat')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    inlines = [KaderProfileInline]
    
    def get_no_hp(self, obj):
        try:
            return obj.kaderprofile.no_hp
        except:
            return '-'
    get_no_hp.short_description = 'No. HP'
    
    def get_alamat(self, obj):
        try:
            return obj.kaderprofile.alamat
        except:
            return '-'
    get_alamat.short_description = 'Alamat'


# Custom Group Admin
class CustomGroupAdmin(GroupAdmin):
    list_display = ('name',)
    search_fields = ('name',)


# Unregister default
admin.site.unregister(User)
admin.site.unregister(Group)

# Register dengan custom
admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)


# Daftarkan KaderProfile
@admin.register(KaderProfile)
class KaderProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'no_hp', 'alamat')
    list_filter = ('user__groups',)
    search_fields = ('user__username', 'user__first_name', 'no_hp', 'alamat')
    raw_id_fields = ('user',)