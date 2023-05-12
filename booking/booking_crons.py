import datetime

from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils import timezone

from booking.models import Booking
from apscheduler.schedulers.blocking import BlockingScheduler

from booking.utils import email_logs

schedule = BlockingScheduler()


def send_email(event_name, event_date, email):
    """
    Send email to user
    """
    rtx = {"event_name": event_name, "event_date": event_date}

    message = get_template("three_days.html").render(rtx)
    email = EmailMessage(
        subject="Booking Reminder",
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
        reply_to=[settings.DEFAULT_FROM_EMAIL],
    )
    email.content_subtype = "html"
    email.send()


@schedule.scheduled_job("interval", minutes=59)
def booking_three_days_reminder():
    booking = Booking.objects.filter(
        status__in=["scheduled", "dispatched"],
        appointment_date_time__lte=timezone.now() + datetime.timedelta(days=3),
        three_day_reminder=False,
    )
    for obj in booking:
        event_name = obj.bod.frequency.service.title
        event_date = obj.appointment_date_time
        email = obj.bod.user.email
        send_email(event_name, event_date, email)
        email_logs(obj.bod.user, "Booking Reminder")
    booking.update(three_day_reminder=True)


@schedule.scheduled_job("interval", minutes=59)
def booking_one_day_reminder():
    booking = Booking.objects.filter(
        status__in=["scheduled", "dispatched"],
        appointment_date_time__lte=timezone.now() + datetime.timedelta(days=1),
        one_day_reminder=False,
    )
    for obj in booking:
        event_name = obj.bod.frequency.service.title
        event_date = obj.appointment_date_time
        email = obj.bod.user.email
        send_email(event_name, event_date, email)
        email_logs(obj.bod.user, "Booking Reminder")
    booking.update(one_day_reminder=True)


@schedule.scheduled_job("interval", minutes=59)
def three_hour_reminder():
    booking = Booking.objects.filter(
        status__in=["scheduled", "dispatched"],
        appointment_date_time__lte=timezone.now() + datetime.timedelta(hours=3),
        three_hour_reminder=False,
    )
    for obj in booking:
        event_name = obj.bod.frequency.service.title
        event_date = obj.appointment_date_time
        email = obj.bod.user.email
        send_email(event_name, event_date, email)
        email_logs(obj.bod.user, "Booking Reminder")
    booking.update(three_hour_reminder=True)


schedule.start()
