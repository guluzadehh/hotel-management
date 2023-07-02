from django.test import TestCase
from django.core.exceptions import ValidationError
from ..factories import RoomFactory, ReservationFactory
from datetime import datetime, timedelta


class RoomTest(TestCase):
    def setUp(self):
        self.room = RoomFactory()

    def test_room_str(self):
        return self.assertEquals(str(self.room), f"Комната {self.room.number}")


class ReservationTest(TestCase):
    def setUp(self):
        self.start_date = datetime(2023, 1, 1).date()
        self.end_date = self.start_date + timedelta(days=2)

    def test_reservation_total_price(self):
        reservation = ReservationFactory(
            start_date=self.start_date, end_date=self.end_date
        )

        total_price = (
            (self.end_date - self.start_date).days + 1
        ) * reservation.room.price_per_day

        self.assertEquals(reservation.total_price, total_price)

    def test_reservation_dates_wrong_order(self):
        ReservationFactory(start_date=self.end_date, end_date=self.start_date)
        self.assertRaises(ValidationError)

    def test_reservation_start_date_lt_today(self):
        ReservationFactory(
            start_date=(datetime.today() - timedelta(days=1)), end_date=self.end_date
        )
        self.assertRaises(ValidationError)

    def test_reservation_end_date_lt_today(self):
        ReservationFactory(
            start_date=self.start_date, end_date=(datetime.today() - timedelta(days=1))
        )
        self.assertRaises(ValidationError)
