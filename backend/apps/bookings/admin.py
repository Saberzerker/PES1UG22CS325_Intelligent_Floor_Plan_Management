from django.contrib import admin
from .models import Booking, UserRoomPreference


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['room', 'user', 'start_time', 'end_time', 'participants_count', 'status']
    list_filter = ['status', 'start_time']
    search_fields = ['user__username', 'room__name']


@admin.register(UserRoomPreference)
class UserRoomPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'room', 'booking_count', 'last_booked']
    readonly_fields = ['booking_count', 'last_booked']