from django.db.models import Q
from rest_framework import permissions, viewsets

from . import permissions as event_permissions
from .models import Event
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        event_permissions.IsEventOrganizerOrInvited,
        event_permissions.OnlyEventOrganizerEditoOrDelete,
    ]

    def get_queryset(self):
        user = self.request.user
        return Event.objects.filter(Q(organizer=user) | Q(invites=user)).distinct()

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)
