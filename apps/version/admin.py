from django.contrib import admin
from .models import Version
# Register your models here.

class VersionAdmin(admin.ModelAdmin):
    list_display = ['android_version', 'ios_version', 'android_update_required', 'ios_update_required']

admin.site.register(Version, VersionAdmin)
