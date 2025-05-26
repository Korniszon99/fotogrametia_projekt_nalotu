from django.urls import path
from . import views

app_name = 'photogrammetry'

urlpatterns = [
    path('', views.flight_planner, name='flight_planner'),
    path('calculate/', views.calculate_flight, name='calculate_flight'),
    path('visualization/', views.generate_visualization, name='visualization'),
]