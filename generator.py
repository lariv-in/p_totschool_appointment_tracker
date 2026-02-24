import random
from datetime import timedelta
from django.utils import timezone
from lariv.generators import BaseGenerator
from lariv.registry import GeneratorRegistry
from users.models import User
from .models import Appointment


APPOINTMENT_NAMES = [
    "Parent-Teacher Meeting",
    "Staff Meeting",
    "Curriculum Review",
    "Student Counseling Session",
    "Department Head Meeting",
    "Board Meeting",
    "Interview - Teaching Position",
    "Interview - Admin Position",
    "Budget Planning Session",
    "Annual Review Meeting",
    "Safety Committee Meeting",
    "PTA Meeting",
    "Sports Day Planning",
    "Cultural Event Planning",
    "Exam Schedule Discussion",
    "New Admission Interview",
    "Scholarship Committee Meeting",
    "Library Committee Meeting",
    "IT Infrastructure Review",
    "Training Workshop",
    "Guest Lecture Coordination",
    "Field Trip Planning",
    "Science Fair Preparation",
    "Art Exhibition Setup",
    "Music Program Rehearsal",
]

LOCATIONS = [
    "Conference Room A",
    "Conference Room B",
    "Principal's Office",
    "Staff Room",
    "Library Meeting Room",
    "Auditorium",
    "Computer Lab",
    "Science Lab",
    "Sports Complex Office",
    "Admin Block - Room 101",
    "Admin Block - Room 202",
    "Main Hall",
    "Counseling Room",
    "HR Office",
    "Finance Office",
]


@GeneratorRegistry.register("appointments.AppointmentGenerator")
class AppointmentGenerator(BaseGenerator):
    dependencies = []

    def clean(self):
        print("Deleting existing appointments")
        Appointment.objects.all().delete()

    def generate_appointments_for_user(self, user: User, count: int):
        """Generate non-overlapping appointments for a user."""
        now = timezone.now()
        # Start from beginning of today
        current_time = now.replace(hour=8, minute=0, second=0, microsecond=0)

        created = 0
        attempts = 0
        max_attempts = count * 3

        while created < count and attempts < max_attempts:
            attempts += 1

            # Random day offset (spread across past 30 days and next 60 days)
            day_offset = random.randint(-30, 60)
            start_time = current_time + timedelta(days=day_offset)

            # Random hour between 8 AM and 5 PM
            dt = start_time.replace(
                hour=random.randint(8, 16),
                minute=random.choice([0, 15, 30, 45]),
            )

            # Check for overlaps
            overlapping = Appointment.objects.filter(
                created_by=user,
                datetime__gt=dt - timedelta(minutes=30),
                datetime__lt=dt + timedelta(minutes=30),
            ).exists()

            if overlapping:
                continue

            Appointment.objects.create(
                created_by=user,
                name=random.choice(APPOINTMENT_NAMES),
                location=random.choice(LOCATIONS),
                datetime=dt,
            )
            created += 1

        return created

    def generate(self):
        users = User.objects.filter(is_active=True)
        if not users.exists():
            print("Error: No active users found.")
            return

        total_created = 0
        for user in users:
            count = random.randint(5, 15)
            created = self.generate_appointments_for_user(user, count)
            total_created += created
            print(f"Generated {created} appointments for {user}")

        print(f"Generated {total_created} total appointments")


def run():
    AppointmentGenerator().run()
