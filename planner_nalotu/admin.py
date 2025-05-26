from django.contrib import admin
from .models import Camera, Aircraft

@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['name', 'focal_length', 'sensor_width', 'sensor_height', 'pixel_size']
    search_fields = ['name']

@admin.register(Aircraft)
class AircraftAdmin(admin.ModelAdmin):
    list_display = ['name', 'cruise_speed', 'max_altitude']
    search_fields = ['name']