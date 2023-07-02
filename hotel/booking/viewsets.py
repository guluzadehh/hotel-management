from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    DestroyAPIView,
    RetrieveAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.filters import OrderingFilter
from .models import Room, Reservation
from .serializers import (
    RoomSerializer,
    DetailedRoomSerializer,
    ReservationSerializer,
    ReservationCreateSerializer,
)
from .permissions import IsSameGuest
from .filters import RoomFilter, ReservationFilter


class RoomListAPIView(ListAPIView):
    serializer_class = RoomSerializer
    filter_backends = [RoomFilter, OrderingFilter]
    ordering_fields = ["beds", "price_per_day"]
    queryset = Room.objects.all()


class RoomRetrieveAPIView(RetrieveAPIView):
    serializer_class = DetailedRoomSerializer
    queryset = Room.objects.all().prefetch_related("reservations")


class ReservationListCreateAPIView(ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Reservation.objects.select_related("room", "guest")
    filter_backends = [ReservationFilter]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return ReservationCreateSerializer
        return ReservationSerializer

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)


class ReservationDestroyAPIView(DestroyAPIView):
    queryset = Reservation.objects.all()
    permission_classes = [IsAdminUser | IsSameGuest]
