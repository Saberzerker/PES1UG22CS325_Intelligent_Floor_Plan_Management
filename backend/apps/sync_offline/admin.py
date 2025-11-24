from django.contrib import admin
from .models import OfflineChange


@admin.register(OfflineChange)
class OfflineChangeAdmin(admin.ModelAdmin):
    list_display = ['user', 'change_type', 'model_name', 'sync_status', 'timestamp']
    list_filter = ['sync_status', 'change_type']
    readonly_fields = ['timestamp', 'synced_at']