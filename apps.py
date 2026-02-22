from django.apps import AppConfig


class TotschoolAppointmentTrackerConfig(AppConfig):
    name = "p_totschool_appointment_tracker"
    p_type = "app"
    verbose_name = "Appointments"
    url_prefix = "appointments"
    icon = "calendar"

    def ready(self):
        from . import ui  # noqa: F401
