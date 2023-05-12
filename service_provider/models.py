from django.db import models

from user_module.models import User


class LeaveTime(models.Model):
    """
    Leave time for service provider. Much like dispatcher.
    """

    service_provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_in_leave"
    )
    start = models.DateTimeField()
    end = models.DateTimeField()
    title = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceProviderTasks(models.Model):
    """
    Tasks for service provider.
    """

    service_provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_in_task"
    )
    description = models.TextField(null=True, blank=True)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


CHOICE_IN_STATUS = [
    ("Pending", "Pending"),
    ("In_Progress", "In_Progress"),
    ("Completed", "Completed"),
]


class ManagerTask(models.Model):
    """
    Tasks for Manager.
    """

    manager = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="manager_in_task"
    )
    description = models.TextField(null=True, blank=True)
    status  = models.CharField(max_length=20, default="Pending")
    is_completed = models.BooleanField(default=False)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ToDoNote(models.Model):
    """Rest Framework testing model"""

    service_provider = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ServiceProviderLocation(models.Model):
    """
    Service provider location.
    """

    service_provider = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_in_location"
    )
    booking = models.ForeignKey(
        "booking.Booking",
        on_delete=models.CASCADE,
        related_name="booking_in_location",
        null=True,
        blank=True,
    )
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    total_hours = models.FloatField(null=True, blank=True)
    latitude = models.CharField(max_length=255)
    longitude = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
