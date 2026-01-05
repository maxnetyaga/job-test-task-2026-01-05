from typing import cast

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .emails import send_event_invitation_email
from .models import Event

User = get_user_model()


class EmailManyToManyField(serializers.ListField):
    def __init__(self, **kwargs):
        kwargs["child"] = serializers.EmailField()
        super().__init__(**kwargs)

    def to_representation(self, value):
        if hasattr(value, "all"):
            return [user.email for user in value.all()]  # pyright: ignore[reportAttributeAccessIssue]

        raise Exception(
            "Model's field doesn't implement Django BaseManager's all() method."
        )


class EventSerializer(serializers.ModelSerializer):
    invites = EmailManyToManyField()
    organizer = serializers.EmailField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "created",
            "title",
            "description",
            "date",
            "location",
            "organizer",
            "invites",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["organizer"] = instance.organizer.email
        return ret

    def validate(self, attrs):
        invites = attrs.get("invites", [])
        organizer_email = None

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            organizer_email = request.user.email

        if self.instance:
            organizer_email = self.instance.organizer.email

        if organizer_email and organizer_email in invites:
            raise serializers.ValidationError(
                {"invites": "The event organizer cannot be invited to their own event."}
            )

        return attrs

    def create(self, validated_data):
        invite_emails = validated_data.pop("invites", [])
        event = Event.objects.create(**validated_data)

        invited_users = User.objects.filter(email__in=invite_emails)
        event.invites.set(invited_users)

        if invited_users.exists():
            send_event_invitation_email(event, invited_users)

        return event

    def update(self, instance, validated_data):
        instance = cast(Event, instance)

        invite_emails = validated_data.pop("invites", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if invite_emails is None:
            return instance

        invited_users = User.objects.filter(email__in=invite_emails)
        request = self.context.get("request")

        if request and request.method == "PUT":
            instance.invites.set(invited_users)
            if not invited_users.exists():
                send_event_invitation_email(instance, invited_users)

        elif request and request.method == "PATCH":
            existing_invites = instance.invites.values_list("id", flat=True)
            new_invites = [
                user
                for user in invited_users
                if user.id not in existing_invites  # pyright: ignore[reportAttributeAccessIssue]
            ]

            instance.invites.add(*new_invites)

            if new_invites:
                send_event_invitation_email(instance, new_invites)

        return instance
