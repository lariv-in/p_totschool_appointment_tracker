from components.menu import MenuItem, Menu
from components.detail import Detail
from components.modals import Modal
from components.tables import (
    TableColumn,
    TableGridContent,
    TableListContent,
    Table,
)
from components.forms import (
    DateInput,
    Form,
    DeleteConfirmation,
    SubmitInput,
    ForeignKeyInput,
    TextareaInput,
    DateTimeInput,
    PhoneInput,
    TextInput,
    ClearInput,
    CheckboxInput,
    ManyToManyInput,
    ShowIf,
)
from components.timeline import Timeline
from components.container import Row, Column
from components.labels import InlineLabel
from components.fields import (
    TextField,
    DateTimeField,
    SubtitleField,
    TitleField,
    ListField,
)
from components.layouts import ScaffoldLayout
from components.charts import Chart
from typing import List
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from lariv.registry import UIRegistry
from components.base import Component
from users.models import User


# Menus
@UIRegistry.register("appointments.AppointmentMenu")
class AppointmentMenu(Component):
    def build(self):
        return Menu(
            uid="appointment-menu",
            title="Appointments",
            back=MenuItem(
                uid="appointment-menu-back",
                title="Back to All Apps",
                url=reverse_lazy("apps"),
            ),
            children=[
                MenuItem(
                    uid="appointment-menu-list",
                    title="All Appointments",
                    url=reverse_lazy("appointments:default"),
                ),
                MenuItem(
                    uid="appointment-menu-cards",
                    title="Appointments Timeline",
                    url=reverse_lazy("appointments:cards"),
                ),
                MenuItem(
                    uid="appointment-menu-create",
                    title="Create Appointment",
                    url=reverse_lazy("appointments:create"),
                ),
            ],
        )


@UIRegistry.register("appointments.AppointmentDetailMenu")
class AppointmentDetailMenu(Component):
    def build(self):
        return Menu(
            uid="appointment-detail-menu",
            back=MenuItem(
                uid="appointment-detail-menu-back",
                title="Back to all Appointments",
                url=reverse_lazy("appointments:default"),
            ),
            key="appointment",
            title=lambda o: f"Appointment: {o.name}",
            children=[
                MenuItem(
                    uid="appointment-detail-menu-detail",
                    title="Appointment Detail",
                    key="appointment",
                    url=lambda o: reverse("appointments:detail", args=[o.pk]),
                ),
                MenuItem(
                    uid="appointment-detail-menu-edit",
                    title="Edit Appointment",
                    key="appointment",
                    url=lambda o: reverse("appointments:update", args=[o.pk]),
                ),
                MenuItem(
                    uid="appointment-detail-menu-delete",
                    title="Delete Appointment",
                    key="appointment",
                    url=lambda o: reverse("appointments:delete", args=[o.pk]),
                ),
            ],
        )


# Filter
@UIRegistry.register("appointments.AppointmentFilter")
class AppointmentFilter(Component):
    def build(self):
        return Form(
            uid="appointment-filter",
            url=reverse_lazy("appointments:default"),
            target="#appointment-table_display_content",
            method="get",
            swap="morph",
            children=[
                DateInput(
                    uid="appointment-filter-date",
                    key="date",
                    label="Date",
                ),
                TextInput(
                    uid="appointment-filter-name",
                    key="name",
                    label="Name",
                ),
                TextInput(
                    uid="appointment-filter-location",
                    key="location",
                    label="Location",
                ),
                ManyToManyInput(
                    uid="appointment-filter-created-by",
                    key="created_by",
                    model=User,
                    label="Created By",
                    url=reverse_lazy("users:multi_select"),
                    role=["totschool_admin"],
                    display_attr="name",
                    placeholder="Select users...",
                ),
                CheckboxInput(
                    uid="appointment-filter-overlapping",
                    key="overlapping",
                    label="Overlaps",
                ),
                Row(
                    uid="appointment-filter-actions",
                    classes="flex gap-2",
                    children=[
                        SubmitInput(
                            uid="appointment-filter-submit",
                            label="Apply Filters",
                        ),
                        ClearInput(
                            uid="appointment-filter-clear",
                            label="Clear",
                        ),
                    ],
                ),
            ],
        )


# Form Fields
@UIRegistry.register("appointments.AppointmentFormFields")
class AppointmentFormFields(Component):
    def build(self):
        return Column(
            uid="appointment-form-fields",
            children=[
                Row(
                    uid="appointment-form-row-1",
                    classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
                    children=[
                        TextInput(
                            uid="appointment-form-name",
                            key="name",
                            label="Name",
                            required=True,
                        ),
                        TextareaInput(
                            uid="appointment-form-location",
                            key="location",
                            label="Location",
                            required=True,
                        ),
                    ],
                ),
                Row(
                    uid="appointment-form-row-2",
                    classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
                    children=[
                        PhoneInput(
                            uid="appointment-form-phone",
                            key="phone",
                            label="Phone",
                            required=True,
                        ),
                        DateTimeInput(
                            uid="appointment-form-datetime",
                            key="datetime",
                            label="Date & Time",
                            required=True,
                        ),
                    ],
                ),
                TextareaInput(
                    uid="appointment-form-remarks",
                    key="remarks",
                    label="Remarks",
                    required=False,
                ),
                ForeignKeyInput(
                    uid="appointment-form-created-by",
                    key="created_by",
                    model=User,
                    label="Created By",
                    url=reverse_lazy("users:select"),
                    display_attr="name",
                    role=["totschool_admin"],
                    placeholder="Select a user...",
                    required=True,
                ),
                SubmitInput(
                    uid="appointment-form-submit",
                    label="Save Appointment",
                ),
            ],
        )


@UIRegistry.register("appointments.AppointmentCreateForm")
class AppointmentCreateForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-create-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentMenu")().build(),
            ],
            children=[
                Form(
                    uid="appointment-create-form",
                    url=reverse_lazy("appointments:create"),
                    target="#app-layout",
                    key="appointment",
                    title="Create Appointment",
                    subtitle="Create a new appointment",
                    classes="@container",
                    children=[
                        UIRegistry.get("appointments.AppointmentFormFields")().build()
                    ],
                )
            ],
        )


@UIRegistry.register("appointments.AppointmentUpdateForm")
class AppointmentUpdateForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-update-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentDetailMenu")().build(),
            ],
            children=[
                Form(
                    uid="appointment-update-form",
                    url=lambda obj: reverse("appointments:update", args=[obj.pk]),
                    target="#app-layout",
                    key="appointment",
                    title="Edit Appointment",
                    subtitle="Update appointment details",
                    classes="@container",
                    children=[
                        UIRegistry.get("appointments.AppointmentFormFields")().build()
                    ],
                )
            ],
        )


# Table
@UIRegistry.register("appointments.AppointmentTable")
class AppointmentTable(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-table-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentMenu")().build(),
            ],
            children=[
                Table(
                    uid="appointment-table",
                    classes="w-full",
                    key="appointments",
                    title="Appointments",
                    displays={
                        "Grid": TableGridContent,
                        "List": TableListContent,
                    },
                    subtitle="List of appointments",
                    create_url=reverse_lazy("appointments:create"),
                    url=lambda o: reverse("appointments:detail", args=[o.pk]),
                    filter_component=UIRegistry.get(
                        "appointments.AppointmentFilter"
                    )().build(),
                    columns=[
                        TableColumn(
                            uid="appointment-col-name",
                            label="Name",
                            key="name",
                            children=[
                                TextField(
                                    uid="appointment-col-name-field",
                                    key="name",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-col-location",
                            label="Location",
                            key="location",
                            children=[
                                TextField(
                                    uid="appointment-col-location-field",
                                    key="location",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-col-phone",
                            label="Phone",
                            key="phone",
                            children=[
                                TextField(
                                    uid="appointment-col-phone-field",
                                    key="phone",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-col-datetime",
                            label="Date & Time",
                            key="datetime",
                            children=[
                                DateTimeField(
                                    uid="appointment-col-datetime-field",
                                    key="datetime",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-col-created-by",
                            label="Created By",
                            key="created_by",
                            role=["totschool_admin"],
                            children=[
                                TextField(
                                    uid="appointment-col-created-by-field",
                                    key="created_by",
                                    role=["totschool_admin"],
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-col-created-at",
                            label="Created At",
                            key="created_at",
                            children=[
                                DateTimeField(
                                    uid="appointment-col-created-at-field",
                                    key="created_at",
                                )
                            ],
                        ),
                    ],
                )
            ],
        )


# Detail
@UIRegistry.register("appointments.AppointmentDetail")
class AppointmentDetail(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-detail-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentDetailMenu")().build(),
            ],
            children=[
                Detail(
                    uid="appointment-detail-view",
                    key="appointment",
                    children=[
                        Column(
                            uid="appointment-detail",
                            children=[
                                ShowIf(
                                    uid="appointment-detail-overlap-warning-alert",
                                    key="overlapping_appointments",
                                    render_cond=lambda c, kwargs: bool(
                                        kwargs.get("overlapping_appointments")
                                    ),
                                    children=[
                                        Row(
                                            classes="alert alert-warning mb-4 shadow-sm items-center gap-4 p-4",
                                            children=[
                                                TextField(
                                                    uid="overlap-warning-msg",
                                                    static_value="⚠️ Warning: This appointment conflicts with existing schedule!",
                                                    classes="font-bold text-xs min-w-32 w-1/5",
                                                ),
                                                ListField(
                                                    uid="appointment-detail-overlap-list",
                                                    key="overlapping_appointments",
                                                    children=[
                                                        Row(
                                                            url=lambda o: o.get_absolute_url(),
                                                            classes="flex gap-2 items-center text-sm link link-primary bg-black/5 border border-black/10 p-1 px-2 rounded-md transition-colors w-fit",
                                                            children=[
                                                                TextField(
                                                                    key="name",
                                                                    classes="font-semibold",
                                                                ),
                                                                TextField(
                                                                    static_value=" - "
                                                                ),
                                                                DateTimeField(
                                                                    key="datetime"
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                            ],
                                        )
                                    ],
                                ),
                                TitleField(
                                    uid="appointment-detail-name",
                                    key="name",
                                ),
                                SubtitleField(
                                    uid="appointment-detail-location",
                                    key="location",
                                ),
                                InlineLabel(
                                    uid="appointment-detail-phone-label",
                                    title="Phone",
                                    classes="mt-2",
                                    children=[
                                        TextField(
                                            uid="appointment-detail-phone",
                                            key="phone",
                                        )
                                    ],
                                ),
                                InlineLabel(
                                    uid="appointment-detail-datetime-label",
                                    title="Date & Time",
                                    classes="mt-2",
                                    children=[
                                        DateTimeField(
                                            uid="appointment-detail-datetime-field",
                                            key="datetime",
                                        )
                                    ],
                                ),
                                InlineLabel(
                                    uid="appointment-detail-created-by-label",
                                    title="Created By",
                                    role=["totschool_admin"],
                                    children=[
                                        TextField(
                                            uid="appointment-detail-created-by-field",
                                            role=["totschool_admin"],
                                            key="created_by",
                                        )
                                    ],
                                ),
                                InlineLabel(
                                    uid="appointment-detail-remarks",
                                    title="Remarks",
                                    children=[
                                        TextField(
                                            uid="appointment-detail-remarks",
                                            key="remarks",
                                        )
                                    ],
                                ),
                                InlineLabel(
                                    uid="appointment-detail-created-at-label",
                                    title="Created At",
                                    role=["totschool_admin"],
                                    children=[
                                        DateTimeField(
                                            uid="appointment-detail-created-at-field",
                                            role=["totschool_admin"],
                                            key="created_at",
                                        )
                                    ],
                                ),
                            ],
                        ),
                    ],
                )
            ],
        )


# Delete Form
@UIRegistry.register("appointments.AppointmentDeleteForm")
class AppointmentDeleteForm(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-delete-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentDetailMenu")().build(),
            ],
            children=[
                DeleteConfirmation(
                    uid="appointment-delete-confirmation",
                    key="appointment",
                    title="Confirm Deletion",
                    message="Are you sure you want to delete this appointment?",
                    cancel_url=lambda obj: reverse(
                        "appointments:detail", args=[obj.pk]
                    ),
                ),
            ],
        )


# Selection Table for Foreign Key inputs
@UIRegistry.register("appointments.AppointmentSelectionTable")
class AppointmentSelectionTable(Component):
    def build(self):
        return Modal(
            uid="appointment-selection-modal",
            title="Select Appointment",
            children=[
                Table(
                    uid="appointment-selection-table",
                    key="appointments",
                    select="single",
                    value_key="pk",
                    display_key="name",
                    columns=[
                        TableColumn(
                            uid="appointment-sel-col-name",
                            label="Name",
                            key="name",
                            children=[
                                TextField(
                                    uid="appointment-sel-name-field",
                                    key="name",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-sel-col-location",
                            label="Location",
                            key="location",
                            children=[
                                TextField(
                                    uid="appointment-sel-location-field",
                                    key="location",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-sel-col-phone",
                            label="Phone",
                            key="phone",
                            children=[
                                TextField(
                                    uid="appointment-sel-phone-field",
                                    key="phone",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-sel-col-datetime",
                            label="Date & Time",
                            key="datetime",
                            children=[
                                DateTimeField(
                                    uid="appointment-sel-datetime-field",
                                    key="datetime",
                                )
                            ],
                        ),
                        TableColumn(
                            uid="appointment-sel-col-created-at",
                            label="Created At",
                            key="created_at",
                            children=[
                                DateTimeField(
                                    uid="appointment-sel-created-at-field",
                                    key="created_at",
                                )
                            ],
                        ),
                    ],
                ),
            ],
        )


# Card Timeline Filter
@UIRegistry.register("appointments.AppointmentCardTimelineFilter")
class AppointmentCardTimelineFilter(Component):
    def build(self):
        return Form(
            uid="appointment-card-timeline-filter",
            url=reverse_lazy("appointments:cards"),
            target="#appointment-card-timeline",
            method="get",
            swap="outerHTML",
            hx_trigger="change",
            classes="flex items-center gap-2",
            children=[
                DateInput(
                    uid="appointment-card-timeline-filter-date",
                    key="date",
                    label="",
                ),
            ],
        )


# Card Timeline (using Timeline component)
@UIRegistry.register("appointments.AppointmentCardTimeline")
class AppointmentCardTimeline(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-card-timeline-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentMenu")().build(),
            ],
            children=[
                Timeline(
                    uid="appointment-card-timeline",
                    key="appointments",
                    title="Appointments",
                    filter_component=UIRegistry.get(
                        "appointments.AppointmentCardTimelineFilter"
                    )().build(),
                    url=lambda o: o.get_absolute_url(),
                    classes="max-h-[80vh]",
                    children=[
                        Column(
                            uid="appointment-card-fields",
                            classes="gap-1",
                            children=[
                                TitleField(
                                    uid="appointment-card-name",
                                    key="name",
                                ),
                                SubtitleField(
                                    uid="appointment-card-location",
                                    key="location",
                                ),
                                Row(
                                    uid="appointment-card-times",
                                    classes="gap-4 text-sm text-base-content/70",
                                    children=[
                                        InlineLabel(
                                            uid="appointment-card-datetime-label",
                                            title="Date & Time",
                                            children=[
                                                DateTimeField(
                                                    uid="appointment-card-datetime-field",
                                                    key="datetime",
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                                InlineLabel(
                                    uid="appointment-card-phone-label",
                                    title="Phone",
                                    children=[
                                        TextField(
                                            uid="appointment-card-phone-field",
                                            key="phone",
                                        )
                                    ],
                                ),
                                TextField(
                                    uid="appointment-card-remarks",
                                    key="remarks",
                                    classes="text-sm text-base-content/60 mt-2",
                                ),
                            ],
                        )
                    ],
                ),
            ],
        )


# Timeline Chart
@UIRegistry.register("appointments.AppointmentTimeline")
class AppointmentTimeline(Component):
    def build(self):
        return ScaffoldLayout(
            uid="appointment-timeline-scaffold",
            sidebar_children=[
                UIRegistry.get("appointments.AppointmentMenu")().build(),
            ],
            children=[
                Chart(
                    uid="appointment-timeline-chart",
                    url=reverse_lazy("appointments:timeline"),
                    type="rangeBar",
                    title="Appointments Timeline",
                    subtitle="Schedule of all appointments over time",
                    filter_component=UIRegistry.get(
                        "appointments.AppointmentFilter"
                    )().build(),
                    options={
                        "chart": {
                            "zoom": {
                                "enabled": True,
                                "type": "x",
                            },
                            "toolbar": {
                                "show": True,
                                "tools": {
                                    "zoom": True,
                                    "zoomin": True,
                                    "zoomout": True,
                                    "pan": True,
                                    "reset": True,
                                },
                            },
                        },
                        "plotOptions": {"bar": {"horizontal": True}},
                        "xaxis": {"type": "datetime"},
                        "tooltip": {"x": {"format": "dd MMM yyyy HH:mm"}},
                    },
                )
            ],
        )
