from rest_framework import serializers
from .models import Room, Reservation
from .exceptions import ConflictException
from operator import attrgetter
from datetime import timedelta
from account.serializers import UserSerializer


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ("id", "number", "price_per_day", "beds")


class DetailedRoomSerializer(RoomSerializer):
    reserved_dates = serializers.SerializerMethodField()

    class Meta:
        model = RoomSerializer.Meta.model
        fields = RoomSerializer.Meta.fields + ("reserved_dates",)

    def get_reserved_dates(self, obj):
        dates = ()

        for reservation in obj.reservations.all():
            start_date = reservation.start_date
            end_date = reservation.end_date

            while start_date <= end_date:
                dates += (attrgetter(*("year", "month", "day"))(start_date),)
                start_date += timedelta(days=1)

        return dates


class ReservationSerializer(serializers.ModelSerializer):
    room = RoomSerializer(read_only=True)
    guest = UserSerializer(read_only=True)

    class Meta:
        model = Reservation
        fields = ("id", "guest", "room", "start_date", "end_date", "total_price")


class ReservationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("room", "start_date", "end_date")

    def validate(self, attrs):
        if attrs["start_date"] > attrs["end_date"]:
            raise serializers.ValidationError("Неверная последовательность дат.")

        room_id = attrs["room"]
        start_date = attrs["start_date"]
        end_date = attrs["end_date"]

        if Reservation.objects.reserved_for(room_id, start_date, end_date).exists():
            raise ConflictException("Комната на этот интервал уже забронирована.")

        return attrs
