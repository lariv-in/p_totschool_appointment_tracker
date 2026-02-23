from django.urls import reverse_lazy, reverse
from lariv.registry import UIRegistry, ComponentRegistry
from users.models import User


# Menus
UIRegistry.register("appointments.AppointmentMenu")(
    ComponentRegistry.get("menu")(
        uid="appointment-menu",
        title="Appointments",
        back=ComponentRegistry.get("menu_item")(
            uid="appointment-menu-back",
            title="Back to All Apps",
            url=reverse_lazy("apps"),
        ),
        children=[
            ComponentRegistry.get("menu_item")(
                uid="appointment-menu-timeline",
                title="Timeline",
                url=reverse_lazy("appointments:timeline"),
            ),
            ComponentRegistry.get("menu_item")(
                uid="appointment-menu-list",
                title="All Appointments",
                url=reverse_lazy("appointments:default"),
            ),
        ],
    )
)

UIRegistry.register("appointments.AppointmentDetailMenu")(
    ComponentRegistry.get("menu")(
        uid="appointment-detail-menu",
        back=ComponentRegistry.get("menu_item")(
            uid="appointment-detail-menu-back",
            title="Back to all Appointments",
            url=reverse_lazy("appointments:default"),
        ),
        key="appointment",
        title=lambda o: f"Appointment: {o.name}",
        children=[
            ComponentRegistry.get("menu_item")(
                uid="appointment-detail-menu-detail",
                title="Appointment Detail",
                key="appointment",
                url=lambda o: reverse("appointments:detail", args=[o.pk]),
            ),
            ComponentRegistry.get("menu_item")(
                uid="appointment-detail-menu-edit",
                title="Edit Appointment",
                key="appointment",
                url=lambda o: reverse("appointments:update", args=[o.pk]),
            ),
            ComponentRegistry.get("menu_item")(
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
    ComponentRegistry.get("form")(
        uid="appointment-filter",
        action=reverse_lazy("appointments:default"),
        target="#appointment-table_display_content",
        method="get",
        swap="morph",
        children=[
            ComponentRegistry.get("date_input")(
                uid="appointment-filter-date",
                key="date",
                label="Date",
            ),
            ComponentRegistry.get("text_input")(
                uid="appointment-filter-name",
                key="name",
                label="Name",
            ),
            ComponentRegistry.get("text_input")(
                uid="appointment-filter-location",
                key="location",
                label="Location",
            ),
            ComponentRegistry.get("foreign_key_input")(
                uid="appointment-filter-created-by",
                key="created_by",
                model=User,
                label="Created By",
                selection_url=reverse_lazy("users:select"),
                display_attr="name",
                placeholder="Select a user...",
            ),
            ComponentRegistry.get("row")(
                uid="appointment-filter-actions",
                classes="flex gap-2",
                children=[
                    ComponentRegistry.get("submit_input")(
                        uid="appointment-filter-submit",
                        label="Apply Filters",
                    ),
                    ComponentRegistry.get("clear_input")(
                        uid="appointment-filter-clear",
                        label="Clear",
                    ),
                ],
            ),
        ],
    )
)


# Form (shared between create and update)
UIRegistry.register("appointments.AppointmentFormFields")(
    ComponentRegistry.get("form")(
        uid="appointment-form",
        action=lambda obj: reverse("appointments:update", args=[obj.pk])
        if obj
        else reverse("appointments:create"),
        target="#app-layout",
        key="appointment",
        title="Appointment Form",
        subtitle="Create or edit an appointment",
        classes="@container",
        children=[
            ComponentRegistry.get("row")(
                uid="appointment-form-row-1",
                classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
                children=[
                    ComponentRegistry.get("text_input")(
                        uid="appointment-form-name",
                        key="name",
                        label="Name",
                        required=True,
                    ),
                    ComponentRegistry.get("text_input")(
                        uid="appointment-form-location",
                        key="location",
                        label="Location",
                        required=True,
                    ),
                ],
            ),
            ComponentRegistry.get("row")(
                uid="appointment-form-row-2",
                classes="grid grid-cols-1 gap-1 @md:grid-cols-2",
                children=[
                    ComponentRegistry.get("datetime_input")(
                        uid="appointment-form-start",
                        key="start",
                        label="Start",
                        required=True,
                    ),
                    ComponentRegistry.get("datetime_input")(
                        uid="appointment-form-end",
                        key="end",
                        label="End",
                        required=True,
                    ),
                ],
            ),
            ComponentRegistry.get("foreign_key_input")(
                uid="appointment-form-created-by",
                key="created_by",
                model=User,
                label="Created By",
                selection_url=reverse_lazy("users:select"),
                display_attr="name",
                placeholder="Select a user...",
                required=True,
            ),
            ComponentRegistry.get("submit_input")(
                uid="appointment-form-submit",
                label="Save Appointment",
            ),
        ],
    )
)

UIRegistry.register("appointments.AppointmentCreateForm")(
    ComponentRegistry.get("scaffold")(
        uid="appointment-create-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[UIRegistry.get("appointments.AppointmentFormFields")],
    )
)

UIRegistry.register("appointments.AppointmentUpdateForm")(
    ComponentRegistry.get("scaffold")(
        uid="appointment-update-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[UIRegistry.get("appointments.AppointmentFormFields")],
    )
)


# Table
UIRegistry.register("appointments.AppointmentTable")(
    ComponentRegistry.get("scaffold")(
        uid="appointment-table-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[
            ComponentRegistry.get("table")(
                uid="appointment-table",
                classes="w-full",
                key="appointments",
                title="Appointments",
                subtitle="List of appointments",
                create_url=reverse_lazy("appointments:create"),
                row_url=lambda o: reverse("appointments:detail", args=[o.pk]),
                filter_component=UIRegistry.get("appointments.AppointmentFilter"),
                columns=[
                    ComponentRegistry.get("table_column")(
                        uid="appointment-col-name",
                        label="Name",
                        key="name",
                        component=ComponentRegistry.get("text_field")(
                            uid="appointment-col-name-field",
                            key="name",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-col-location",
                        label="Location",
                        key="location",
                        component=ComponentRegistry.get("text_field")(
                            uid="appointment-col-location-field",
                            key="location",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-col-start",
                        label="Start",
                        key="start",
                        component=ComponentRegistry.get("date_field")(
                            uid="appointment-col-start-field",
                            key="start",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-col-end",
                        label="End",
                        key="end",
                        component=ComponentRegistry.get("date_field")(
                            uid="appointment-col-end-field",
                            key="end",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-col-created-by",
                        label="Created By",
                        key="created_by",
                        component=ComponentRegistry.get("text_field")(
                            uid="appointment-col-created-by-field",
                            key="created_by",
                        ),
                    ),
                ],
            )
        ],
    )
)


# Detail
UIRegistry.register("appointments.AppointmentDetail")(
    ComponentRegistry.get("scaffold")(
        uid="appointment-detail-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[
            ComponentRegistry.get("detail")(
                uid="appointment-detail-view",
                key="appointment",
                children=[
                    ComponentRegistry.get("column")(
                        uid="appointment-detail",
                        children=[
                            ComponentRegistry.get("title_field")(
                                uid="appointment-detail-name",
                                key="name",
                            ),
                            ComponentRegistry.get("subtitle_field")(
                                uid="appointment-detail-location",
                                key="location",
                            ),
                            ComponentRegistry.get("inline_label")(
                                uid="appointment-detail-start-label",
                                title="Start",
                                classes="mt-2",
                                component=ComponentRegistry.get("date_field")(
                                    uid="appointment-detail-start-field",
                                    key="start",
                                ),
                            ),
                            ComponentRegistry.get("inline_label")(
                                uid="appointment-detail-end-label",
                                title="End",
                                component=ComponentRegistry.get("date_field")(
                                    uid="appointment-detail-end-field",
                                    key="end",
                                ),
                            ),
                            ComponentRegistry.get("inline_label")(
                                uid="appointment-detail-created-by-label",
                                title="Created By",
                                component=ComponentRegistry.get("text_field")(
                                    uid="appointment-detail-created-by-field",
                                    key="created_by",
                                ),
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
    ComponentRegistry.get("scaffold")(
        uid="appointment-delete-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentDetailMenu"),
        ],
        children=[
            ComponentRegistry.get("delete_confirmation")(
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
    ComponentRegistry.get("modal")(
        uid="appointment-selection-modal",
        title="Select Appointment",
        children=[
            ComponentRegistry.get("selection_table")(
                uid="appointment-selection-table",
                key="appointments",
                value_key="pk",
                display_key="name",
                columns=[
                    ComponentRegistry.get("table_column")(
                        uid="appointment-sel-col-name",
                        label="Name",
                        key="name",
                        component=ComponentRegistry.get("text_field")(
                            uid="appointment-sel-name-field",
                            key="name",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-sel-col-location",
                        label="Location",
                        key="location",
                        component=ComponentRegistry.get("text_field")(
                            uid="appointment-sel-location-field",
                            key="location",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-sel-col-start",
                        label="Start",
                        key="start",
                        component=ComponentRegistry.get("date_field")(
                            uid="appointment-sel-start-field",
                            key="start",
                        ),
                    ),
                    ComponentRegistry.get("table_column")(
                        uid="appointment-sel-col-end",
                        label="End",
                        key="end",
                        component=ComponentRegistry.get("date_field")(
                            uid="appointment-sel-end-field",
                            key="end",
                        ),
                    ),
                ],
            ),
        ],
    )
)


# Timeline Chart
UIRegistry.register("appointments.AppointmentTimeline")(
    ComponentRegistry.get("scaffold")(
        uid="appointment-timeline-scaffold",
        sidebar_children=[
            UIRegistry.get("appointments.AppointmentMenu"),
        ],
        children=[
            ComponentRegistry.get("chart")(
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
                    "plotOptions": {
                        "bar": {
                            "horizontal": True
                        }
                    },
                    "xaxis": {
                        "type": "datetime"
                    },
                    "tooltip": {
                        "x": {
                            "format": "dd MMM yyyy HH:mm"
                        }
                    },
                }
            )
        ],
    )
)
