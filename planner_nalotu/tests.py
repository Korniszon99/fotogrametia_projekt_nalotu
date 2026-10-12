from django.test import TestCase, Client
from .models import Camera, Aircraft
from .views import FlightPlanCalculator
import json

class FlightPlanTests(TestCase):
    def setUp(self):
        self.camera = Camera.objects.create(name='Test', focal_length=50, sensor_width=36, sensor_height=24, pixel_size=5)
        self.aircraft = Aircraft.objects.create(name='Test', min_speed=100, max_speed=200, max_altitude=5000)

    def test_physical_units_and_overlap(self):
        result = FlightPlanCalculator(1000, 1000, 0.05, self.camera, self.aircraft).calculate_flight_parameters()
        self.assertEqual(result['flight_height'], 500)
        self.assertEqual(result['ground_coverage_x'], 360)
        self.assertEqual(result['ground_coverage_y'], 240)
        self.assertGreaterEqual(result['corrected_overlap_q'], 0.3)
        expected = result['corrected_strips'] * (1000 + 2 * 360) / (150 * 1000 / 3600)
        self.assertAlmostEqual(result['flight_time'], expected, places=2)

    def test_custom_altitude_changes_gsd_and_coverage(self):
        result = FlightPlanCalculator(1000, 1000, 0.05, self.camera, self.aircraft, altitude=1000).calculate_flight_parameters()
        self.assertEqual(result['gsd'], 0.1)
        self.assertEqual(result['ground_coverage_x'], 720)

    def test_invalid_parameters_and_resource_limit(self):
        for width, gsd in [(0, 0.05), (-1, 0.05), (float('nan'), 0.05), (1000, 0), (10000000, 0.00001)]:
            with self.assertRaises(ValueError):
                FlightPlanCalculator(width, 1000, gsd, self.camera, self.aircraft).calculate_flight_parameters()

    def test_post_validation_and_csrf(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.get('/calculate/').status_code, 405)
        self.assertEqual(client.post('/calculate/', data='{}', content_type='application/json').status_code, 403)
        client.get('/')
        csrf = client.cookies['csrftoken'].value
        payload = {'area_width':1000, 'area_height':1000, 'gsd':0.05, 'camera':self.camera.pk, 'aircraft':self.aircraft.pk}
        response = client.post('/calculate/', data=json.dumps(payload), content_type='application/json', HTTP_X_CSRFTOKEN=csrf)
        self.assertEqual(response.status_code, 200)
        payload['area_width'] = 0
        self.assertEqual(client.post('/calculate/', data=json.dumps(payload), content_type='application/json', HTTP_X_CSRFTOKEN=csrf).status_code, 400)
