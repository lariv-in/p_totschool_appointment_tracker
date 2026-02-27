from django.db import models
from django.urls import reverse
from users.models import User
from datetime import timedelta
from phonenumber_field.modelfields import PhoneNumberField


class Appointment(models.Model):
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    name = models.CharField(max_length=250)
    location = models.TextField(max_length=250)
    datetime = models.DateTimeField()
    phone = PhoneNumberField(blank=True, null=True)
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("appointments:detail", kwargs={"pk": self.pk})


    def get_overlapping_appointments(self):
        """Return appointments that overlap with this one for the same user."""
        if not self.created_by or not self.datetime:
            return Appointment.objects.none()
        return Appointment.objects.filter(
            created_by=self.created_by,
            datetime__gte=self.datetime - timedelta(minutes=30),
            datetime__lte=self.datetime + timedelta(minutes=30)
        ).exclude(pk=self.pk)

    def has_overlaps(self):
        """Check if this appointment overlaps with any other."""
        return self.get_overlapping_appointments().exists()

    class Meta:
        ordering = ["-datetime"]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
