from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Event(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    title = models.TextField()
    description = models.TextField(null=True)
    date = models.DateTimeField()
    location = models.TextField()
    organizer = models.ForeignKey(
        User, on_delete=models.DO_NOTHING, related_name="organized_event"
    )
    invites = models.ManyToManyField(
        User, through="EventInvite", related_name="invited_event"
    )

    def __str__(self) -> str:
        return f"{self.title} ({self.pk})"


class EventInvite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    state = models.TextField(
        default="PENDING",
        choices=models.TextChoices("EventInviteState", "PENDING ACCEPTED"),
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "event"],
                name="unique_user_event_invite",
            )
        ]

    def __str__(self) -> str:
        return f"{self.event.title} ({self.event.pk}) | {self.user} ({self.pk})"
