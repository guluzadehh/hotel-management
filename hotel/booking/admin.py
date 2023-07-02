from django.contrib import admin
from .models import Room, Reservation


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ["number", "price_per_day", "beds"]


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ["guest", "room", "created_at", "start_date", "end_date"]
