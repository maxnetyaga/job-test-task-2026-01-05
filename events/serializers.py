from typing import cast

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Event

User = get_user_model()


class EmailManyToManyField(serializers.ListField):
    def __init__(self, **kwargs):
        kwargs["child"] = serializers.EmailField()
        super().__init__(**kwargs)

    def to_representation(self, value):
        if hasattr(value, "all"):
            return [user.email for user in value.all()]

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

        return event

    def update(self, instance, validated_data):
        instance = cast(Event, instance)

        invite_emails = validated_data.pop("invites", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if invite_emails is not None:
            invited_users = User.objects.filter(email__in=invite_emails)
            request = self.context.get("request")

            if request and request.method == "PUT":
                instance.invites.set(invited_users)
            elif request and request.method == "PATCH":
                instance.invites.add(*invited_users)

        return instance
