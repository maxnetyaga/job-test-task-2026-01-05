from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import permissions as event_permissions
from .models import Event, EventInvite
from .serializers import EventSerializer


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        event_permissions.IsEventOrganizerOrInvited,
        event_permissions.OnlyEventOrganizerEditoOrDelete,
    ]

    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

    @extend_schema(request=None)
    @action(
        detail=True,
        methods=["post"],
        url_path="submit-invitation",
        permission_classes=[event_permissions.IsEventInvited],
    )
    def submit_event_invitation(self, request, pk=None):
        event = self.get_object()

        invitation = get_object_or_404(
            EventInvite,
            user=request.user,
            event=event,
        )

        if invitation.state == "ACCEPTED":
            return Response(
                {"detail": "Invitation already accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invitation.state = "ACCEPTED"
        invitation.save(update_fields=["state"])

        return Response(status=status.HTTP_204_NO_CONTENT)
