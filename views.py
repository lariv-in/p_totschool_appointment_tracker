from django.urls import reverse, reverse_lazy
from lariv.mixins import (
    ListViewMixin,
    DetailViewMixin,
    PostFormViewMixin,
    DeleteViewMixin,
    SelectionTableViewMixin,
    ChartViewMixin,
    apply_filters,
)
from lariv.registry import ViewRegistry
from .models import Appointment


@ViewRegistry.register("appointments.AppointmentList")
class AppointmentList(ListViewMixin):
    model = Appointment
    component = "appointments.AppointmentTable"
    key = "appointments"


@ViewRegistry.register("appointments.AppointmentView")
class AppointmentView(DetailViewMixin):
    model = Appointment
    component = "appointments.AppointmentDetail"
    key = "appointment"


@ViewRegistry.register("appointments.AppointmentCreate")
class AppointmentCreate(PostFormViewMixin):
    model = Appointment
    component = "appointments.AppointmentCreateForm"
    key = "appointment"

    def get_success_url(self, obj):
        return reverse("appointments:detail", kwargs={"pk": obj.pk})


@ViewRegistry.register("appointments.AppointmentUpdate")
class AppointmentUpdate(PostFormViewMixin):
    model = Appointment
    component = "appointments.AppointmentUpdateForm"
    key = "appointment"

    def get_success_url(self, obj):
        return reverse("appointments:detail", kwargs={"pk": obj.pk})


@ViewRegistry.register("appointments.AppointmentDelete")
class AppointmentDelete(DeleteViewMixin):
    model = Appointment
    component = "appointments.AppointmentDeleteForm"
    key = "appointment"
    success_url = reverse_lazy("appointments:default")


@ViewRegistry.register("appointments.AppointmentSelectionTable")
class AppointmentSelectionTableView(SelectionTableViewMixin):
    model = Appointment
    component = "appointments.AppointmentSelectionTable"
    key = "appointments"
    title = "Select Appointment"


@ViewRegistry.register("appointments.AppointmentTimeline")
class AppointmentTimeline(ChartViewMixin):
    model = Appointment
    component = "appointments.AppointmentTimeline"
    key = "appointments"

    def get_chart_data(self, request, **kwargs):
        queryset = self.get_queryset()
        
        # Apply filters just like ListViewMixin does
        get_params = request.GET.dict()
        queryset = apply_filters(queryset, get_params, self.model)
        
        # Order by start time
        queryset = queryset.order_by("start")

        # ApexCharts Timeline uses { x: "Name", y: [start_timestamp, end_timestamp] }
        data = []
        for appt in queryset:
            data.append({
                "x": str(appt.created_by) if appt.created_by else "Unknown",
                "y": [
                    int(appt.start.timestamp() * 1000), 
                    int(appt.end.timestamp() * 1000)
                ],
                "url": reverse("appointments:detail", kwargs={"pk": appt.pk}),
                "details": {
                    "name": appt.name,
                    "location": appt.location
                }
            })

        return {
            "series": [
                {
                    "name": "Appointments",
                    "data": data
                }
            ]
        }
