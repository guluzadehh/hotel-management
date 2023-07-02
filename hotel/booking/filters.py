from rest_framework.filters import BaseFilterBackend
from django.db.models import OuterRef, Exists
from datetime import timedelta, datetime
from .models import Reservation


class RoomFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        min_price = request.query_params.get("min_price", None)
        if min_price is not None:
            queryset = queryset.filter(price_per_day__gte=min_price)

        max_price = request.query_params.get("max_price", None)
        if max_price is not None:
            print(max_price)
            queryset = queryset.filter(price_per_day__lte=max_price)

        beds = request.query_params.get("beds", None)
        if beds is not None:
            queryset = queryset.filter(beds=beds)

        start_date = request.query_params.get("start_date", None)
        end_date = request.query_params.get("end_date", None)

        try:
            if start_date is not None:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

            if end_date is not None:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        except:
            return queryset

        if start_date and not end_date:
            end_date = start_date + timedelta(days=1)
        elif end_date and not start_date:
            start_date = end_date - timedelta(days=1)

        if start_date and end_date and start_date < end_date:
            queryset = queryset.filter(
                ~Exists(
                    Reservation.objects.reserved_for(
                        OuterRef("pk"), start_date, end_date
                    )
                )
            )

        return queryset


class ReservationFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        if not (request.query_params.get("all", None) and request.user.is_staff):
            return queryset.filter(guest=request.user)
        return queryset
