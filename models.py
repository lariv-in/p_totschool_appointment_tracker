from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from users.models import User
from datetime import datetime


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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("appointments:detail", kwargs={"pk": self.pk})

    def clean(self):
        # Validate end > start
        if isinstance(self.start, datetime) and isinstance(self.end, datetime) and self.end <= self.start:
            raise ValidationError({"end": "End time must be after start time."})

        # Check overlaps for same user
        overlapping = Appointment.objects.filter(
            created_by=self.created_by,
            start__lt=self.end,
            end__gt=self.start,
        ).exclude(pk=self.pk)

        if overlapping.exists():
            raise ValidationError(
                {"start": "Overlaps with an existing appointment."}
            )

    class Meta:
        ordering = ["-start"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
