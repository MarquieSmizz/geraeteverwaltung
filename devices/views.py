from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from .models import Device, DeviceType


class DeviceListView(LoginRequiredMixin, ListView):
    model = Device
    template_name = "devices/home.html"
    context_object_name = "devices"

    def get_queryset(self):
        queryset = Device.objects.select_related(
            "device_type",
            "firmware",
            "adresse",
        ).order_by("seriennummer")

        search_query = self.request.GET.get("q", "").strip()
        device_type_id = self.request.GET.get("device_type", "").strip()

        if search_query:
            queryset = queryset.filter(seriennummer__icontains=search_query)

        if device_type_id:
            queryset = queryset.filter(device_type_id=device_type_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["device_types"] = DeviceType.objects.all().order_by(
            "hersteller",
            "modell",
            "typnummer",
        )
        context["search_query"] = self.request.GET.get("q", "").strip()
        context["selected_device_type"] = self.request.GET.get(
            "device_type",
            "",
        ).strip()
        return context
