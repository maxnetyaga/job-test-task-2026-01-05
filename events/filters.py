from django_filters import rest_framework as filters

from .models import Event


class EventFilter(filters.FilterSet):
    class Meta:
        model = Event
        fields = {
            "title": ["exact", "icontains"],
            "location": ["exact", "icontains"],
            "date": ["exact", "gte", "lte", "gt", "lt"],
        }

    title = filters.CharFilter(lookup_expr="icontains", label="Title contains")
    location = filters.CharFilter(lookup_expr="icontains", label="Location contains")

    date_after = filters.DateTimeFilter(
        field_name="date", lookup_expr="gte", label="Date after"
    )
    date_before = filters.DateTimeFilter(
        field_name="date", lookup_expr="lte", label="Date before"
    )

    organizer_email = filters.CharFilter(
        field_name="organizer__email", lookup_expr="iexact", label="Organizer email"
    )

    invited_user_email = filters.CharFilter(
        field_name="invites__email", lookup_expr="iexact", label="Invited user email"
    )
