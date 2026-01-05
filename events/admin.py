from django.contrib import admin

from .models import Event, EventInvite


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    pass


@admin.register(EventInvite)
class EventInviteAdmin(admin.ModelAdmin):
    pass
