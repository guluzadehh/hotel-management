import factory
from .models import Room, Reservation
from account.factories import UserFactory
from datetime import datetime, timedelta
import random


class RoomFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Room

    number = factory.Sequence(lambda n: n)
    price_per_day = factory.Sequence(lambda n: (n + 1) * 20)
    beds = factory.LazyAttribute(lambda o: random.randint(1, 5))


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    guest = factory.SubFactory(UserFactory)
    room = factory.SubFactory(RoomFactory)
    start_date = datetime.today().date()
    end_date = factory.LazyAttribute(lambda o: o.start_date + timedelta(days=2))
