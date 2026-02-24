from django.urls import path
from lariv.registry import ViewRegistry
from . import views  # noqa: F401 - ensures views are registered

AppointmentList = ViewRegistry.get("appointments.AppointmentList")
AppointmentView = ViewRegistry.get("appointments.AppointmentView")
AppointmentCreate = ViewRegistry.get("appointments.AppointmentCreate")
AppointmentUpdate = ViewRegistry.get("appointments.AppointmentUpdate")
AppointmentDelete = ViewRegistry.get("appointments.AppointmentDelete")
AppointmentSelectionTable = ViewRegistry.get("appointments.AppointmentSelectionTable")

AppointmentTimeline = ViewRegistry.get("appointments.AppointmentTimeline")
AppointmentCardTimeline = ViewRegistry.get("appointments.AppointmentCardTimeline")

app_name = "appointments"

urlpatterns = [
    path("", AppointmentList.as_view(), name="default"),
    path("timeline/", AppointmentTimeline.as_view(), name="timeline"),
    path("cards/", AppointmentCardTimeline.as_view(), name="cards"),
    path("create/", AppointmentCreate.as_view(), name="create"),
    path("<int:pk>/", AppointmentView.as_view(), name="detail"),
    path("<int:pk>/update/", AppointmentUpdate.as_view(), name="update"),
    path("<int:pk>/delete/", AppointmentDelete.as_view(), name="delete"),
    path("select/", AppointmentSelectionTable.as_view(), name="select"),
]
