from django.contrib import admin
from account.models import Profile, Adress, Cards
from django.contrib.auth.models import Group
# Register your models here.

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'gender', 'birthdate', 'is_active', 'is_staff')
    list_filter = ('gender', 'is_active', 'is_staff')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Adress)
admin.site.register(Cards)
