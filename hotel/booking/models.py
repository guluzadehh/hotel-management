from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from account.models import User
from .managers import ReservationQuerySet
from datetime import datetime


class Room(models.Model):
    number = models.PositiveSmallIntegerField(
        "номер", validators=[MinValueValidator(1)])
    price_per_day = models.PositiveSmallIntegerField("цена")
    beds = models.PositiveSmallIntegerField("кол-во мест")

    class Meta:
        verbose_name = "Комната"
        verbose_name_plural = "Комнаты"

    def __str__(self):
        return f"Комната {self.number}"


class Reservation(models.Model):
    guest = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="гость",
        related_name="reservations",
    )
    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        verbose_name="комната",
        related_name="reservations",
    )
    start_date = models.DateField("начало")
    end_date = models.DateField("конец")
    created_at = models.DateTimeField("дата резервации", auto_now=True)

    objects = ReservationQuerySet.as_manager()

    class Meta:
        verbose_name = "Резервация"
        verbose_name_plural = "Резервации"

    def clean(self):
        today = datetime.today()
        if (
            self.start_date > self.end_date
            or self.start_date < today.date()
            or self.end_date < today.date()
        ):
            raise ValidationError("Неверная последовательность дат.")

    @property
    def total_price(self):
        return self.room.price_per_day * ((self.end_date - self.start_date).days + 1)
