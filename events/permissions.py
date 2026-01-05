from typing import cast

from django.contrib.auth.models import User
from rest_framework.permissions import BasePermission

from .models import Event


class OnlyEventOrganizerEditoOrDelete(BasePermission):
    message = "Only organizer can edit event."

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Event):
            raise Exception(
                f"{self.__class__.__name__} can be used only with Event views."
            )

        if request.method not in ["PATCH", "PUT", "DELETE"]:
            return True

        return cast(User, obj.organizer).pk == request.user.pk


class IsEventOrganizer(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Event):
            raise Exception(
                f"{self.__class__.__name__} can be used only with Event views."
            )

        return request.user.pk == cast(User, obj.organizer).pk


class IsEventInvited(BasePermission):
    message = "You are not invited to event"

    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Event):
            raise Exception(
                f"{self.__class__.__name__} can be used only with Event views."
            )

        return request.user.pk in (user.pk for user in obj.invites.all())


class IsEventOrganizerOrInvited(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Event):
            raise Exception(
                f"{self.__class__.__name__} can be used only with Event views."
            )

        return request.user.pk in [
            cast(User, obj.organizer).pk,
            *(user.pk for user in obj.invites.all()),
        ]
