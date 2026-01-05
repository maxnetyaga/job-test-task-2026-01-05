from django.conf import settings
from django.core.mail import send_mail


def send_event_invitation_email(event, invited_users):
    if not invited_users:
        return

    for user in invited_users:
        subject = f"You're invited to: {event.title}"

        message = f"""
            Hello {user.get_full_name() or user.username},

            You have been invited to the following event:

            Event: {event.title}
            Date: {event.date.strftime("%B %d, %Y at %I:%M %p")}
            Location: {event.location}
            Organizer: {event.organizer.get_full_name() or event.organizer.username} ({event.organizer.email})

            Description:
            {event.description or "No description provided"}
        """.strip()

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email to {user.email}: {e!s}")
