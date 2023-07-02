from rest_framework.test import APITestCase
from django.urls import reverse
from ..factories import RoomFactory, ReservationFactory
from account.factories import UserFactory
from ..models import Room, Reservation
from datetime import datetime, timedelta
from operator import attrgetter


class RoomListAPIViewTest(APITestCase):
    def setUp(self):
        self.rooms = RoomFactory.create_batch(4)

    def test_room_list(self):
        res = self.client.get(reverse("api:room-list"))
        self.assertEquals(res.status_code, 200)
        self.assertEquals(len(res.data), len(self.rooms))

    def test_filter_min_price_room_list(self):
        res = self.client.get(reverse("api:room-list"), {"min_price": 60})
        self.assertEqual(res.status_code, 200)
        self.assertEquals(
            len(res.data), len(Room.objects.filter(price_per_day__gte=60))
        )
        for room in res.data:
            self.assertTrue(room["price_per_day"] >= 60)

    def test_filter_max_price_room_list(self):
        res = self.client.get(reverse("api:room-list"), {"max_price": 60})
        self.assertEqual(res.status_code, 200)
        self.assertEquals(
            len(res.data), len(Room.objects.filter(price_per_day__lte=60))
        )
        for room in res.data:
            self.assertTrue(room["price_per_day"] <= 60)

    def test_filter_beds_room_list(self):
        room = RoomFactory(beds=2)
        res = self.client.get(reverse("api:room-list"), {"beds": 2})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), len(Room.objects.filter(beds=2)))
        for room in res.data:
            self.assertEqual(room["beds"], 2)

    def test_filter_start_date_room_list(self):
        today = datetime.today().date()
        start_date = today + timedelta(days=5)

        self.rooms += [RoomFactory(), RoomFactory()]
        ReservationFactory(
            room=self.rooms[-1],
            start_date=start_date,
            end_date=start_date + timedelta(days=2),
        )
        ReservationFactory(
            room=self.rooms[-2],
            start_date=start_date - timedelta(days=2),
            end_date=start_date + timedelta(days=2),
        )

        res = self.client.get(
            reverse("api:room-list"), {"start_date": start_date.strftime("%Y-%m-%d")}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), len(self.rooms) - 2)

    def test_filter_end_date_room_list(self):
        today = datetime.today().date()
        end_date = today + timedelta(days=7)

        self.rooms += [RoomFactory(), RoomFactory()]
        ReservationFactory(
            room=self.rooms[-1],
            end_date=end_date,
            start_date=end_date - timedelta(days=2),
        )
        ReservationFactory(
            room=self.rooms[-2],
            end_date=end_date + timedelta(days=2),
            start_date=end_date - timedelta(days=2),
        )

        res = self.client.get(
            reverse("api:room-list"), {"end_date": end_date.strftime("%Y-%m-%d")}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), len(self.rooms) - 2)


class RoomDetailTest(APITestCase):
    def setUp(self):
        self.room = RoomFactory()

    def test_reserved_dates_room_detail(self):
        today = datetime.today().date()

        reserved_dates = []

        start_date1 = today + timedelta(days=2)
        end_date1 = today + timedelta(days=4)

        ReservationFactory(room=self.room, start_date=start_date1, end_date=end_date1)

        while start_date1 < end_date1:
            reserved_dates.append(attrgetter(*("year", "month", "day"))(start_date1))
            start_date1 += timedelta(days=1)

        start_date2 = today + timedelta(days=6)
        end_date2 = today + timedelta(days=10)

        ReservationFactory(room=self.room, start_date=start_date2, end_date=end_date2)

        while start_date2 < end_date2:
            reserved_dates.append(attrgetter(*("year", "month", "day"))(start_date2))
            start_date2 += timedelta(days=1)

        res = self.client.get(reverse("api:room-detail", args=[self.room.id]))
        self.assertEqual(res.status_code, 200)
        for reserved_date in reserved_dates:
            self.assertTrue(reserved_date in res.data["reserved_dates"])


class ReservationListTest(APITestCase):
    def setUp(self):
        self.admin = UserFactory(is_staff=True)
        self.user = UserFactory()
        ReservationFactory.create_batch(3, guest=self.admin)
        ReservationFactory.create_batch(2, guest=self.user)

    def test_list_reservation_unauth(self):
        res = self.client.get(reverse("api:reservation-list"))
        self.assertEqual(res.status_code, 403)

    def test_list_reservation(self):
        self.client.force_login(self.admin)
        res = self.client.get(reverse("api:reservation-list"))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            len(res.data), len(Reservation.objects.filter(guest=self.admin))
        )

    def test_list_reservation_all(self):
        self.client.force_login(self.admin)
        res = self.client.get(reverse("api:reservation-list"), {"all": "true"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), len(Reservation.objects.all()))

    def test_list_reservation_all_not_staff(self):
        self.client.force_login(self.user)
        res = self.client.get(reverse("api:reservation-list"), {"all": "true"})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            len(res.data), len(Reservation.objects.filter(guest=self.user))
        )


class ReservationCreateTest(APITestCase):
    def setUp(self):
        self.room = RoomFactory()
        self.user = UserFactory()

    def test_reservation_create_unauth(self):
        today = datetime.today().date()
        res = self.client.post(
            reverse("api:reservation-list"),
            {
                "room": self.room.id,
                "start_date": today + timedelta(days=2),
                "end_date": today + timedelta(days=4),
            },
        )
        self.assertEqual(res.status_code, 403)

    def test_reservation_create_dates_unordered(self):
        today = datetime.today().date()
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api:reservation-list"),
            {
                "room": self.room.id,
                "start_date": today + timedelta(days=4),
                "end_date": today + timedelta(days=2),
            },
        )
        self.assertEqual(res.status_code, 400)
        self.assertEqual(
            res.data["non_field_errors"][0], "Неверная последовательность дат."
        )

    def test_reservation_create_with_existing_reservation(self):
        today = datetime.today().date()
        start_date = today + timedelta(days=2)
        end_date = today + timedelta(days=4)
        ReservationFactory(room=self.room, start_date=start_date, end_date=end_date)
        self.client.force_login(self.user)
        res = self.client.post(
            reverse("api:reservation-list"),
            {
                "room": self.room.id,
                "start_date": start_date - timedelta(days=1),
                "end_date": end_date + timedelta(days=1),
            },
        )

        self.assertEqual(res.status_code, 409)
        self.assertEqual(
            res.data["detail"], "Комната на этот интервал уже забронирована."
        )


class ReservationDestroyTest(APITestCase):
    def setUp(self):
        self.user = UserFactory()
        self.reservation = ReservationFactory(guest=self.user)

    def test_reservation_destroy_unauth(self):
        res = self.client.delete(
            reverse("api:reservation-detail", args=[self.reservation.id])
        )
        self.assertEqual(res.status_code, 403)

    def test_reservation_destroy_other(self):
        self.client.force_login(self.user)
        res = self.client.delete(
            reverse("api:reservation-detail", args=[ReservationFactory().id])
        )
        self.assertEqual(res.status_code, 403)
        self.assertEqual(
            res.data["detail"],
            "У вас недостаточно прав для выполнения данного действия.",
        )

    def test_reservation_destroy_staff(self):
        admin = UserFactory(is_staff=True)
        self.client.force_login(admin)
        res = self.client.delete(
            reverse("api:reservation-detail", args=[self.reservation.id])
        )
        self.assertEqual(res.status_code, 204)

    def test_reservation_destroy_own(self):
        self.client.force_login(self.user)
        res = self.client.delete(
            reverse("api:reservation-detail", args=[self.reservation.id])
        )
        self.assertEqual(res.status_code, 204)
