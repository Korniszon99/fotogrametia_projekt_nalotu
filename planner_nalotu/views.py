import math
import json
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from io import BytesIO
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Camera, Aircraft


class FlightPlanCalculator:
    def __init__(self, area_width, area_height, gsd, camera, aircraft, altitude=None, speed=None):
        self.Dx = area_width  # m
        self.Dy = area_height  # m
        self.gsd = gsd  # m/pixel
        self.camera = camera
        self.aircraft = aircraft
        self.user_altitude = altitude  # User-provided altitude (m)
        self.user_speed = speed  # User-provided speed (km/h)

        # Standardowe pokrycia
        self.p_target = 0.6  # pokrycie wzdłużne
        self.q_target = 0.3  # pokrycie poprzeczne

    def calculate_flight_parameters(self):
        # Wysokość lotu - użyj podanej przez użytkownika lub oblicz
        if self.user_altitude:
            self.W = self.user_altitude
        else:
            self.W = (self.camera.focal_length * self.gsd * 1000) / self.camera.pixel_size

        # Zasięgi terenowe zdjęć
        self.Lx = (self.camera.sensor_width * self.gsd * 1000) / self.camera.pixel_size
        self.Ly = (self.camera.sensor_height * self.gsd * 1000) / self.camera.pixel_size

        # Bazy zdjęć
        self.Bx = self.Lx * (1 - self.p_target)
        self.By = self.Ly * (1 - self.q_target)

        # Nominalna liczba szeregów
        self.nominal_strips = self.Dy / self.By

        # Skorygowana liczba szeregów
        self.corrected_strips = math.ceil(self.nominal_strips)

        # Skorygowane bazy
        if self.corrected_strips > 1:
            self.corrected_By = self.Dy / (self.corrected_strips - 1)
        else:
            self.corrected_By = self.Dy

        # Liczba zdjęć w szeregu
        self.photos_per_strip = math.ceil(self.Dx / self.Bx) + 1

        # Skorygowane pokrycia
        self.corrected_q = 1 - (self.corrected_By / self.Ly) if self.Ly > 0 else 0
        self.corrected_p = 1 - (self.Bx / self.Lx) if self.Lx > 0 else 0

        # Całkowita liczba zdjęć
        self.total_photos = self.corrected_strips * self.photos_per_strip

        # Długość trasy lotu
        strip_length = self.Dx + 2 * self.Lx  # z zapasem
        total_flight_distance = self.corrected_strips * strip_length

        # Czas lotu - użyj podanej przez użytkownika prędkości lub domyślnej
        speed = self.user_speed if self.user_speed else self.aircraft.cruise_speed
        self.flight_time = total_flight_distance / (speed * 1000 / 3600)  # sekundy

        return {
            'flight_height': round(self.W, 3),
            'ground_coverage_x': round(self.Lx, 3),
            'ground_coverage_y': round(self.Ly, 3),
            'base_x': round(self.Bx, 3),
            'base_y': round(self.By, 3),
            'nominal_strips': round(self.nominal_strips, 3),
            'corrected_strips': self.corrected_strips,
            'corrected_base_y': round(self.corrected_By, 3),
            'corrected_overlap_p': round(self.corrected_p, 3),
            'corrected_overlap_q': round(self.corrected_q, 3),
            'photos_per_strip': self.photos_per_strip,
            'total_photos': self.total_photos,
            'flight_time': round(self.flight_time, 3)
        }


def flight_planner(request):
    cameras = Camera.objects.all()
    aircraft = Aircraft.objects.all()

    # Jeśli nie ma danych w bazie, dodaj przykładowe
    if not cameras.exists():
        Camera.objects.create(
            name="Z/I DMC IIe 140",
            focal_length=92.0,
            sensor_width=12096 * 7.2 / 1000,  # przeliczanie z px i μm na mm
            sensor_height=11200 * 7.2 / 1000,
            pixel_size=7.2
        )

        Camera.objects.create(
            name="Z/I DMC IIe 230",
            focal_length=92.0,
            sensor_width=15552 * 5.6 / 1000,
            sensor_height=14444 * 5.6 / 1000,
            pixel_size=5.6
        )

        Camera.objects.create(
            name="UltraCam Falcon",
            focal_length=70.0,
            sensor_width=14430 * 7.2 / 1000,
            sensor_height=9420 * 7.2 / 1000,
            pixel_size=7.2
        )

        Camera.objects.create(
            name="UltraCam Hawk",
            focal_length=70.0,
            sensor_width=11704 * 6.0 / 1000,
            sensor_height=7920 * 6.0 / 1000,
            pixel_size=6.0
        )
        cameras = Camera.objects.all()

    if not aircraft.exists():
        Aircraft.objects.create(
            name="Cessna 402 (MGGP Aero)",
            min_speed=132,
            max_speed=428,
            max_altitude=8200  # poprawiona wartość z "82oo" na 8200
        )

        Aircraft.objects.create(
            name="Cessna 402 (MGGP Aero) - wersja 2",
            min_speed=100,
            max_speed=280,
            max_altitude=4785
        )

        Aircraft.objects.create(
            name="Vulcan Air P68 Observer 2 (OPEGIEKA Elblag)",
            min_speed=135,
            max_speed=275,
            max_altitude=6100  # poprawiona wartość z "61oo" na 6100
        )

        Aircraft.objects.create(
            name="Zencam MMA (Airborne Technologies)",
            min_speed=120,
            max_speed=267,
            max_altitude=4572
        )

        aircraft = Aircraft.objects.all()

    return render(request, 'photogrammetry/flight_planner.html', {
        'cameras': cameras,
        'aircraft': aircraft
    })


@csrf_exempt
def calculate_flight(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            area_width = float(data['area_width'])
            area_height = float(data['area_height'])
            gsd = float(data['gsd'])
            camera_id = int(data['camera'])
            aircraft_id = int(data['aircraft'])
            altitude = float(data['altitude']) if 'altitude' in data else None
            speed = float(data['speed']) if 'speed' in data else None

            camera = Camera.objects.get(id=camera_id)
            aircraft = Aircraft.objects.get(id=aircraft_id)

            calculator = FlightPlanCalculator(area_width, area_height, gsd, camera, aircraft, altitude, speed)
            results = calculator.calculate_flight_parameters()

            return JsonResponse({
                'success': True,
                'results': results,
                'camera_name': camera.name,
                'aircraft_name': aircraft.name
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@csrf_exempt
def generate_visualization(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            area_width = float(data['area_width'])
            area_height = float(data['area_height'])
            gsd = float(data['gsd'])
            camera_id = int(data['camera'])
            aircraft_id = int(data['aircraft'])
            altitude = float(data['altitude']) if 'altitude' in data else None
            speed = float(data['speed']) if 'speed' in data else None

            camera = Camera.objects.get(id=camera_id)
            aircraft = Aircraft.objects.get(id=aircraft_id)

            calculator = FlightPlanCalculator(area_width, area_height, gsd, camera, aircraft, altitude, speed)
            results = calculator.calculate_flight_parameters()

            # Generowanie wizualizacji
            fig, ax = plt.subplots(1, 1, figsize=(12, 8))

            # Obszar do sfotografowania
            area_rect = patches.Rectangle((0, 0), area_width, area_height,
                                          linewidth=3, edgecolor='red', facecolor='lightcoral', alpha=0.3)
            ax.add_patch(area_rect)

            # Zasięgi zdjęć i trasa lotu
            Lx = results['ground_coverage_x']
            Ly = results['ground_coverage_y']
            By_corrected = results['corrected_base_y']
            strips = results['corrected_strips']
            photos_per_strip = results['photos_per_strip']
            Bx = results['base_x']

            # Rysowanie szeregów i zdjęć
            for strip in range(strips):
                y_pos = strip * By_corrected if strips > 1 else area_height / 2

                # Linia trasy lotu
                flight_line_start = -Lx / 2
                flight_line_end = area_width + Lx / 2
                ax.plot([flight_line_start, flight_line_end], [y_pos, y_pos],
                        'b-', linewidth=2, label='Trasa lotu' if strip == 0 else "")

                # Pozycje zdjęć
                for photo in range(photos_per_strip):
                    x_pos = photo * Bx - Lx / 2

                    # Prostokąt reprezentujący zdjęcie
                    photo_rect = patches.Rectangle((x_pos, y_pos - Ly / 2), Lx, Ly,
                                                   linewidth=1, edgecolor='blue',
                                                   facecolor='lightblue', alpha=0.2)
                    ax.add_patch(photo_rect)

                    # Punkt centrum zdjęcia
                    ax.plot(x_pos + Lx / 2, y_pos, 'bo', markersize=4)

            # Ustawienia wykresu
            margin = max(area_width, area_height) * 0.1
            ax.set_xlim(-Lx / 2 - margin, area_width + Lx / 2 + margin)
            ax.set_ylim(-Ly / 2 - margin, area_height + Ly / 2 + margin)

            ax.set_xlabel('Odległość X [m]', fontsize=12)
            ax.set_ylabel('Odległość Y [m]', fontsize=12)
            ax.set_title(f'Plan nalotu fotogrametrycznego\n{camera.name} | {aircraft.name}', fontsize=14)
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')

            # Legenda
            legend_elements = [
                patches.Patch(color='lightcoral', alpha=0.3, label='Obszar do sfotografowania'),
                patches.Patch(color='lightblue', alpha=0.2, label='Zasięg zdjęć'),
                plt.Line2D([0], [0], color='blue', linewidth=2, label='Trasa lotu'),
                plt.Line2D([0], [0], marker='o', color='blue', markersize=4, linestyle='None', label='Centrum zdjęć')
            ]
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))

            # Dodanie parametrów jako tekst
            params_text = f"""Parametry nalotu:
Wysokość lotu: {results['flight_height']:.1f} m
Liczba szeregów: {results['corrected_strips']}
Zdjęć w szeregu: {results['photos_per_strip']}
Całkowita liczba zdjęć: {results['total_photos']}
Pokrycie wzdłużne: {results['corrected_overlap_p']:.1%}
Pokrycie poprzeczne: {results['corrected_overlap_q']:.1%}
Czas lotu: {results['flight_time']:.1f} min"""

            ax.text(0.02, 0.98, params_text, transform=ax.transAxes, fontsize=10,
                    verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

            plt.tight_layout()

            # Konwersja do base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            plt.close()

            graphic = base64.b64encode(image_png)
            graphic = graphic.decode('utf-8')

            return JsonResponse({
                'success': True,
                'image': graphic,
                'results': results
            })

        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
