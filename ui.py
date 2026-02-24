from typing import List
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from lariv.registry import UIRegistry
from components.base import Component
from users.models import User
from components import *  # noqa


class OverlapWarning(Component):
    """Shows a warning when appointments overlap, with optional confirmation checkbox."""

    def __init__(
        self,
        uid: str = "",
        classes: str = "",
        show_confirmation: bool = True,
        role: List[str] = [],
    ):
        super().__init__(classes, uid, role)
        self.show_confirmation = show_confirmation

    def render_html(self, **kwargs) -> str:
        if not kwargs.get("show_overlap_warning"):
            return ""

        overlapping = kwargs.get("overlapping_appointments", [])
        if not overlapping:
            return ""

        items_html = ""
        for appt in overlapping:
            dt = timezone.localtime(appt.datetime)

            items_html += (
                f'<li><a href="{appt.get_absolute_url()}" class="link">{appt.name}</a> '
                f"({dt.strftime('%b %d %H:%M')})</li>"
            )

        confirmation_html = ""
        if self.show_confirmation:
            confirmation_html = """
            <div class="flex gap-2 mt-2">
                <input type="checkbox" name="confirm_overlap" value="true" class="checkbox checkbox-sm" id="confirm-overlap-checkbox" />
                <label for="confirm-overlap-checkbox" class="text-sm">I understand and want to save anyway</label>
            </div>
            """

        return f"""
        <div id="{self.uid}" class="bg-warning p-4 rounded-box border border-base-300 my-4 flex flex-col">
            <div>
                <div>
                    <h3 class="font-bold">Overlapping Appointments</h3>
                    <p class="text-sm">This appointment overlaps with:</p>
                    <ul class="list-disc list-inside text-sm mt-1">{items_html}</ul>
                </div>
            </div>
            {confirmation_html}
        </div>
        """


# Menus
UIRegistry.register("appointments.AppointmentMenu")(
    Menu(
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
)

UIRegistry.register("appointments.AppointmentDetailMenu")(
    Menu(
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
)


# Filter
UIRegistry.register("appointments.AppointmentFilter")(
    Form(
        uid="appointment-filter",
        action=reverse_lazy("appointments:default"),
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
                selection_url=reverse_lazy("users:multi_select"),
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
)


# Form Fields
UIRegistry.register("appointments.AppointmentFormFields")(
    Column(
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
                        required=False,
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
                selection_url=reverse_lazy("users:select"),
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
)

UIRegistry.register("appointments.AppointmentCreateForm")(
    ScaffoldLayout(
        uid="appointment-create-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[
            Form(
                uid="appointment-create-form",
                action=reverse_lazy("appointments:create"),
                target="#app-layout",
                key="appointment",
                title="Create Appointment",
                subtitle="Create a new appointment",
                classes="@container",
                children=[UIRegistry.get("appointments.AppointmentFormFields")],
            )
        ],
    )
)

UIRegistry.register("appointments.AppointmentUpdateForm")(
    ScaffoldLayout(
        uid="appointment-update-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[
            Form(
                uid="appointment-update-form",
                action=lambda obj: reverse("appointments:update", args=[obj.pk]),
                target="#app-layout",
                key="appointment",
                title="Edit Appointment",
                subtitle="Update appointment details",
                classes="@container",
                children=[UIRegistry.get("appointments.AppointmentFormFields")],
            )
        ],
    )
)


# Table
UIRegistry.register("appointments.AppointmentTable")(
    ScaffoldLayout(
        uid="appointment-table-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
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
                row_url=lambda o: reverse("appointments:detail", args=[o.pk]),
                filter_component=UIRegistry.get("appointments.AppointmentFilter"),
                columns=[
                    TableColumn(
                        uid="appointment-col-name",
                        label="Name",
                        key="name",
                        component=TextField(
                            uid="appointment-col-name-field",
                            key="name",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-col-location",
                        label="Location",
                        key="location",
                        component=TextField(
                            uid="appointment-col-location-field",
                            key="location",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-col-phone",
                        label="Phone",
                        key="phone",
                        component=TextField(
                            uid="appointment-col-phone-field",
                            key="phone",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-col-datetime",
                        label="Date & Time",
                        key="datetime",
                        component=DateTimeField(
                            uid="appointment-col-datetime-field",
                            key="datetime",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-col-created-by",
                        label="Created By",
                        key="created_by",
                        role=["totschool_admin"],
                        component=TextField(
                            uid="appointment-col-created-by-field",
                            key="created_by",
                            role=["totschool_admin"],
                        ),
                    ),
                ],
            )
        ],
    )
)


# Detail
UIRegistry.register("appointments.AppointmentDetail")(
    ScaffoldLayout(
        uid="appointment-detail-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[
            Detail(
                uid="appointment-detail-view",
                key="appointment",
                children=[
                    Column(
                        uid="appointment-detail",
                        children=[
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
                                component=TextField(
                                    uid="appointment-detail-phone",
                                    key="phone",
                                ),
                            ),
                            InlineLabel(
                                uid="appointment-detail-datetime-label",
                                title="Date & Time",
                                classes="mt-2",
                                component=DateTimeField(
                                    uid="appointment-detail-datetime-field",
                                    key="datetime",
                                ),
                            ),
                            InlineLabel(
                                uid="appointment-detail-created-by-label",
                                title="Created By",
                                role=["totschool_admin"],
                                component=TextField(
                                    uid="appointment-detail-created-by-field",
                                    role=["totschool_admin"],
                                    key="created_by",
                                ),
                            ),
                            InlineLabel(
                                uid="appointment-detail-remarks",
                                title="Remarks",
                                component=TextField(
                                    uid="appointment-detail-remarks",
                                    key="remarks",
                                ),
                            ),
                            OverlapWarning(
                                uid="appointment-detail-overlap-warning",
                                show_confirmation=False,
                            ),
                        ],
                    ),
                ],
            )
        ],
    )
)


# Delete Form
UIRegistry.register("appointments.AppointmentDeleteForm")(
    ScaffoldLayout(
        uid="appointment-delete-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[
            DeleteConfirmation(
                uid="appointment-delete-confirmation",
                key="appointment",
                title="Confirm Deletion",
                message="Are you sure you want to delete this appointment?",
                cancel_url=lambda obj: reverse("appointments:detail", args=[obj.pk]),
            ),
        ],
    )
)


# Selection Table for Foreign Key inputs
UIRegistry.register("appointments.AppointmentSelectionTable")(
    Modal(
        uid="appointment-selection-modal",
        title="Select Appointment",
        children=[
            SelectionTable(
                uid="appointment-selection-table",
                key="appointments",
                value_key="pk",
                display_key="name",
                columns=[
                    TableColumn(
                        uid="appointment-sel-col-name",
                        label="Name",
                        key="name",
                        component=TextField(
                            uid="appointment-sel-name-field",
                            key="name",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-sel-col-location",
                        label="Location",
                        key="location",
                        component=TextField(
                            uid="appointment-sel-location-field",
                            key="location",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-sel-col-phone",
                        label="Phone",
                        key="phone",
                        component=TextField(
                            uid="appointment-sel-phone-field",
                            key="phone",
                        ),
                    ),
                    TableColumn(
                        uid="appointment-sel-col-datetime",
                        label="Date & Time",
                        key="datetime",
                        component=DateTimeField(
                            uid="appointment-sel-datetime-field",
                            key="datetime",
                        ),
                    ),
                ],
            ),
        ],
    )
)


# Card Timeline Filter
UIRegistry.register("appointments.AppointmentCardTimelineFilter")(
    Form(
        uid="appointment-card-timeline-filter",
        action=reverse_lazy("appointments:cards"),
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
)


# Card Timeline (using Timeline component)
UIRegistry.register("appointments.AppointmentCardTimeline")(
    ScaffoldLayout(
        uid="appointment-card-timeline-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[
            Timeline(
                uid="appointment-card-timeline",
                key="appointments",
                title="Appointments",
                filter_component=UIRegistry.get(
                    "appointments.AppointmentCardTimelineFilter"
                ),
                row_url=lambda o: o.get_absolute_url(),
                classes="max-h-[80vh]",
                fields=Column(
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
                                    component=DateTimeField(
                                        uid="appointment-card-datetime-field",
                                        key="datetime",
                                    ),
                                ),
                            ],
                        ),
                        InlineLabel(
                            uid="appointment-card-phone-label",
                            title="Phone",
                            component=TextField(
                                uid="appointment-card-phone-field",
                                key="phone",
                            ),
                        ),
                        TextField(
                            uid="appointment-card-remarks",
                            key="remarks",
                            classes="text-sm text-base-content/60 mt-2",
                        ),
                    ],
                ),
            ),
        ],
    )
)


# Timeline Chart
UIRegistry.register("appointments.AppointmentTimeline")(
    ScaffoldLayout(
        uid="appointment-timeline-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[
            Chart(
                uid="appointment-timeline-chart",
                url=reverse_lazy("appointments:timeline"),
                type="rangeBar",
                title="Appointments Timeline",
                subtitle="Schedule of all appointments over time",
                filter_component=UIRegistry.get("appointments.AppointmentFilter"),
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
)
