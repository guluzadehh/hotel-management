from django.db.models import QuerySet, Q


class ReservationQuerySet(QuerySet):
    def reserved_for(self, room_id, start_date, end_date):
        return self.filter(
            Q(room_id=room_id)
            & Q(
                Q(Q(start_date__lte=start_date) & Q(end_date__gte=start_date))
                | Q(Q(start_date__lte=end_date) & Q(end_date__gte=end_date))
                | Q(Q(start_date__gte=start_date) & Q(start_date__lte=end_date))
                | Q(Q(end_date__gte=start_date) & Q(end_date__lte=end_date))
            )
        )
