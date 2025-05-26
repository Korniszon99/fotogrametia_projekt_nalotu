from django.db import models


class Camera(models.Model):
    name = models.CharField(max_length=100)
    focal_length = models.FloatField()  # mm
    sensor_width = models.FloatField()  # mm
    sensor_height = models.FloatField()  # mm
    pixel_size = models.FloatField()  # μm

    def __str__(self):
        return self.name


class Aircraft(models.Model):
    name = models.CharField(max_length=100)
    min_speed = models.FloatField()  # km/h
    max_speed = models.FloatField()  # km/h
    max_altitude = models.FloatField()  # m

    @property
    def cruise_speed(self):
        return (self.min_speed + self.max_speed) / 2

    def __str__(self):
        return self.name
