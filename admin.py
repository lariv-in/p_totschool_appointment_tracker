from django.contrib import admin
from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("name", "location", "start", "end", "created_by")
    search_fields = ("name", "location", "created_by__name")
    list_filter = ("created_by", "start")
    date_hierarchy = "start"
