from django.test import TestCase
from django.utils import timezone
from datetime import timedelta, date, time
from decimal import Decimal
from apps.accounts.models import User
from apps.properties.models import Wing, Unit
from apps.amenities.models import Amenity, AmenityBooking, EVChargingStation, EVChargingSession

class AmenityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='amenity_user', password='Password123!', role=User.Role.RESIDENT)
        self.wing = Wing.objects.create(name='Wing A', code='A')
        self.unit = Unit.objects.create(wing=self.wing, unit_number='A-501', primary_resident=self.user)
        self.amenity = Amenity.objects.create(
            name='Badminton Court 1',
            slug='badminton-court-1',
            hourly_rate=Decimal('100.00'),
            capacity=4
        )
        self.ev_station = EVChargingStation.objects.create(
            station_name='EV Test Bay',
            power_kw=Decimal('22.0'),
            kwh_rate=Decimal('12.00')
        )

    def test_booking_conflict(self):
        today = timezone.now().date()
        AmenityBooking.objects.create(
            amenity=self.amenity,
            resident=self.user,
            unit=self.unit,
            booking_date=today,
            start_time=time(10, 0),
            end_time=time(11, 0),
            status=AmenityBooking.Status.CONFIRMED
        )

        self.client.login(username='amenity_user', password='Password123!')
        response = self.client.post(f'/amenities/{self.amenity.slug}/', {
            'unit': self.unit.id,
            'booking_date': today,
            'start_time': '10:30',
            'end_time': '11:30',
            'guest_count': 2,
            'purpose': 'Game'
        })
        bookings_count = AmenityBooking.objects.filter(amenity=self.amenity, booking_date=today).count()
        self.assertEqual(bookings_count, 1)

    def test_ev_charging_session(self):
        self.client.login(username='amenity_user', password='Password123!')
        response = self.client.post('/amenities/ev-charging/', {
            'station_id': self.ev_station.id,
            'unit_id': self.unit.id,
            'hours': 2
        })
        self.assertEqual(response.status_code, 302)
        sess = EVChargingSession.objects.filter(user=self.user).first()
        self.assertIsNotNone(sess)
        self.assertEqual(sess.status, EVChargingSession.SessionStatus.ACTIVE)
