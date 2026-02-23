from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
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


class OverlapWarningMixin:
    """Mixin to handle overlap warnings for appointments."""

    def check_overlaps(self, obj):
        """Check for overlapping appointments and return them."""
        return obj.get_overlapping_appointments()

    def post(self, request, *args, **kwargs):
        from types import SimpleNamespace
        from components.forms import ManyToManyInput

        pk = kwargs.get("pk")
        instance = self.get_object(pk)
        inputs = self.get_inputs()

        # Get form data
        data = {}
        m2m_data = {}
        for input_comp in inputs:
            field = input_comp.key
            if input_comp.is_instance_of(ManyToManyInput):
                values = request.POST.getlist(f"{input_comp.uid}_values")
                m2m_data[field] = values
                data[field] = values
            else:
                value = request.POST.get(field)
                data[field] = value

        # Validate
        cleaned_data, errors = self.validate(data, inputs, instance)

        if errors:
            return self._render_form_errors(request, kwargs, errors, data, instance)

        # Separate M2M fields
        m2m_cleaned = {}
        regular_cleaned = {}
        for field, value in cleaned_data.items():
            if field in m2m_data:
                m2m_cleaned[field] = value
            else:
                regular_cleaned[field] = value

        # Create a temporary object to check overlaps
        temp_obj = Appointment(pk=pk, **regular_cleaned)

        # Check for overlaps
        overlapping = self.check_overlaps(temp_obj)
        confirm_overlap = request.POST.get("confirm_overlap") == "true"

        if overlapping.exists() and not confirm_overlap:
            # Show warning with overlapping appointments
            prepared_data = self.prepare_data(request, **kwargs)
            prepared_data["overlapping_appointments"] = overlapping
            prepared_data["show_overlap_warning"] = True

            # Preserve form data
            prepared_data[self.get_key()] = instance

            return self.render_component(request, **prepared_data)

        # Proceed with save
        try:
            if instance:
                for field, value in regular_cleaned.items():
                    setattr(instance, field, value)
                instance.save()
                obj = instance
            else:
                obj = self.model.objects.create(**regular_cleaned)

            for field, values in m2m_cleaned.items():
                getattr(obj, field).set(values)

        except ValidationError as e:
            if hasattr(e, "message_dict"):
                for field, msg_list in e.message_dict.items():
                    errors[field] = ", ".join(msg_list)
            else:
                errors["Error"] = str(e)
            return self._render_form_errors(request, kwargs, errors, data, instance)
        except Exception as e:
            errors["Error"] = str(e)
            return self._render_form_errors(request, kwargs, errors, data, instance)

        success_url = self.get_success_url(obj)
        if request.htmx:
            return HttpResponse(status=200, headers={"HX-Redirect": success_url})
        return redirect(success_url)


@ViewRegistry.register("appointments.AppointmentList")
class AppointmentList(ListViewMixin):
    model = Appointment
    component = "appointments.AppointmentTable"
    key = "appointments"

    def prepare_data(self, request, **kwargs):
        from django.db.models import Exists, OuterRef
        from django.core.paginator import Paginator

        queryset = self.get_queryset()
        get_params = request.GET.dict()
        if not (
            self.request.user.is_superuser
            or self.request.user.role in ["totschool_admin"]
        ):
            queryset = queryset.filter(created_by=self.request.user)

        page_number = get_params.pop("page", 1)
        sort = get_params.pop("sort", None)
        if sort is not None:
            queryset = queryset.order_by(sort)

        # Handle overlapping appointments filter
        show_overlapping = get_params.pop("overlapping", None)
        if show_overlapping in ("true", "True", "1", True):
            overlapping_subquery = Appointment.objects.filter(
                created_by=OuterRef("created_by"),
                start__lt=OuterRef("end"),
                end__gt=OuterRef("start"),
            ).exclude(pk=OuterRef("pk"))
            queryset = queryset.annotate(
                has_overlap=Exists(overlapping_subquery)
            ).filter(has_overlap=True)

        queryset = apply_filters(queryset, get_params, self.model)

        paginator = Paginator(queryset, self.get_paginate_by(request))
        page = paginator.page(page_number)

        return {self.get_key(): page}


@ViewRegistry.register("appointments.AppointmentView")
class AppointmentView(DetailViewMixin):
    model = Appointment
    component = "appointments.AppointmentDetail"
    key = "appointment"

    def prepare_data(self, request, **kwargs):
        data = super().prepare_data(request, **kwargs)
        appointment = data[self.get_key()]
        overlapping = appointment.get_overlapping_appointments()
        if overlapping.exists():
            data["overlapping_appointments"] = overlapping
            data["show_overlap_warning"] = True
        return data


@ViewRegistry.register("appointments.AppointmentCreate")
class AppointmentCreate(OverlapWarningMixin, PostFormViewMixin):
    model = Appointment
    component = "appointments.AppointmentCreateForm"
    key = "appointment"

    def validate(self, data, inputs, instance=None):
        data["created_by"] = self.request.user.id
        cleaned_data, errors = super().validate(data, inputs, instance)

        return cleaned_data, errors

    def get_success_url(self, obj):
        return reverse("appointments:detail", kwargs={"pk": obj.pk})


@ViewRegistry.register("appointments.AppointmentUpdate")
class AppointmentUpdate(OverlapWarningMixin, PostFormViewMixin):
    model = Appointment
    component = "appointments.AppointmentUpdateForm"
    key = "appointment"

    def validate(self, data, inputs, instance=None):
        if not (self.request.user.is_superuser or instance.created_by is not self.request.user):
            raise PermissionDenied("You cannot perform this action")

        data["created_by"] = self.request.user.id
        cleaned_data, errors = super().validate(data, inputs, instance)

        return cleaned_data, errors

    def get_success_url(self, obj):
        return reverse("appointments:detail", kwargs={"pk": obj.pk})


@ViewRegistry.register("appointments.AppointmentDelete")
class AppointmentDelete(DeleteViewMixin):
    model = Appointment
    component = "appointments.AppointmentDeleteForm"
    key = "appointment"
    success_url = reverse_lazy("appointments:default")

    def get_queryset(self):
        if not (self.request.user.is_superuser or self.request.user.role in ["totschool_admin"]):
            super().get_queryset().filter(created_by=self.request.user)
        super().get_queryset()


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
        from datetime import datetime

        queryset = self.get_queryset()


        # Apply filters just like ListViewMixin does
        get_params = request.GET.dict()

        # Handle range-based filtering (from chart zoom/pan)
        range_min = get_params.pop("range_min", None)
        range_max = get_params.pop("range_max", None)

        # Handle many-to-many created_by filter (multiple values)
        created_by_values = request.GET.getlist("appointment-filter-created-by_values")

        # Check if any filters are provided
        has_filters = bool(range_min and range_max) or bool(created_by_values) or any(v for v in get_params.values())

        if not (
            self.request.user.is_superuser
            or self.request.user.role in ["totschool_admin"]
        ):
            queryset = queryset.filter(created_by=self.request.user)
            has_filters = True

        if not has_filters:
            return {
                "series": [{"name": "Appointments", "data": []}],
                "noData": {"text": "Please apply filters to view appointments"}
            }

        if range_min and range_max:
            # Parse ISO format datetime strings (from chart zoom/pan)
            try:
                from datetime import timedelta

                min_dt = datetime.fromisoformat(range_min.replace("Z", "+00:00"))
                max_dt = datetime.fromisoformat(range_max.replace("Z", "+00:00"))

                # Add 25% buffer on each side so user can zoom out if no/little data visible
                range_duration = max_dt - min_dt
                buffer = range_duration * 0.25
                min_dt = min_dt - buffer
                max_dt = max_dt + buffer

                queryset = queryset.filter(start__gte=min_dt, start__lte=max_dt)
            except ValueError:
                pass

        # Handle date range filter from form
        start_date = get_params.pop("start_date", None)
        end_date = get_params.pop("end_date", None)

        if start_date:
            queryset = queryset.filter(start__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start__date__lte=end_date)

        # Handle many-to-many created_by filter (multiple values)
        if created_by_values:
            queryset = queryset.filter(created_by__in=created_by_values)
            # Remove from get_params so apply_filters doesn't try to handle it
            get_params.pop("appointment-filter-created-by_values", None)

        # Handle overlapping appointments filter
        show_overlapping = get_params.pop("overlapping", None)
        if show_overlapping in ("true", "True", "1", True):
            # Get IDs of appointments that have overlaps
            from django.db.models import Exists, OuterRef
            overlapping_subquery = Appointment.objects.filter(
                created_by=OuterRef("created_by"),
                start__lt=OuterRef("end"),
                end__gt=OuterRef("start"),
            ).exclude(pk=OuterRef("pk"))
            queryset = queryset.annotate(
                has_overlap=Exists(overlapping_subquery)
            ).filter(has_overlap=True)

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
