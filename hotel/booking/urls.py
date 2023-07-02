from django.urls import path
from .views import RoomListView, ReservationListView


urlpatterns = [
    path("", RoomListView.as_view(), name="home"),
    path("rooms/", RoomListView.as_view(), name="room-list"),
    path("reservations/", ReservationListView.as_view(), name="reservation-list"),
]
