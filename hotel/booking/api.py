from django.urls import path
from .viewsets import (
    RoomListAPIView,
    RoomRetrieveAPIView,
    ReservationListCreateAPIView,
    ReservationDestroyAPIView,
)

app_name = "booking"

urlpatterns = [
    path("rooms/", RoomListAPIView.as_view(), name="room-list"),
    path("rooms/<int:pk>/", RoomRetrieveAPIView.as_view(), name="room-detail"),
    path(
        "reservations/", ReservationListCreateAPIView.as_view(), name="reservation-list"
    ),
    path(
        "reservations/<int:pk>/",
        ReservationDestroyAPIView.as_view(),
        name="reservation-detail",
    ),
]
