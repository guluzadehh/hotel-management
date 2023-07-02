from typing import Any, Dict
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Room


class RoomListView(TemplateView):
    template_name = "booking/rooms.html"

    def get_context_data(self, **kwargs):
        beds_list = (
            Room.objects.values_list("beds", flat=True).order_by("beds").distinct()
        )

        return {"beds_list": beds_list}


class ReservationListView(TemplateView):
    template_name = "booking/reservations.html"
