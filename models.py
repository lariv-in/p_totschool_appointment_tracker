from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from users.models import User
from datetime import datetime
from phonenumber_field.modelfields import PhoneNumberField


class Appointment(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    name = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    start = models.DateTimeField()
    end = models.DateTimeField()
    phone = PhoneNumberField(blank=True, null=True)
    remarks = models.TextField(blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("appointments:detail", kwargs={"pk": self.pk})

    def clean(self):
        # Validate end > start
        if isinstance(self.start, datetime) and isinstance(self.end, datetime) and self.end <= self.start:
            raise ValidationError({"end": "End time must be after start time."})

    def get_overlapping_appointments(self):
        """Return appointments that overlap with this one for the same user."""
        if not self.created_by or not self.start or not self.end:
            return Appointment.objects.none()
        return Appointment.objects.filter(
            created_by=self.created_by,
            start__lt=self.end,
            end__gt=self.start,
        ).exclude(pk=self.pk)

    def has_overlaps(self):
        """Check if this appointment overlaps with any other."""
        return self.get_overlapping_appointments().exists()

    class Meta:
        ordering = ["-start"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
