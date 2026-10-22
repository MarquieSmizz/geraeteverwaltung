from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import AdresseForm, DeviceTypeForm, FirmwareForm
from .models import Adresse, Device, DeviceType, Firmware


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
            queryset = queryset.filter(
                seriennummer__icontains=search_query
            )

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


class DeviceTypeListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    model = DeviceType
    template_name = "devices/devicetype_list.html"
    context_object_name = "device_types"
    permission_required = "devices.view_devicetype"
    raise_exception = True

    def get_queryset(self):
        queryset = DeviceType.objects.all().order_by(
            "hersteller",
            "klasse",
            "modell",
            "typnummer",
        )
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(hersteller__icontains=search_query)
                | Q(klasse__icontains=search_query)
                | Q(modell__icontains=search_query)
                | Q(typnummer__icontains=search_query)
            )

        return queryset


class DeviceTypeCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = DeviceType
    form_class = DeviceTypeForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.add_devicetype"
    success_url = reverse_lazy("devices:devicetype-list")
    raise_exception = True


class DeviceTypeUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = DeviceType
    form_class = DeviceTypeForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.change_devicetype"
    success_url = reverse_lazy("devices:devicetype-list")
    raise_exception = True


class FirmwareListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    model = Firmware
    template_name = "devices/firmware_list.html"
    context_object_name = "firmwares"
    permission_required = "devices.view_firmware"
    raise_exception = True

    def get_queryset(self):
        queryset = Firmware.objects.all().order_by(
            "firmware_name",
            "version",
        )
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(firmware_name__icontains=search_query)
                | Q(version__icontains=search_query)
            )

        return queryset


class FirmwareCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = Firmware
    form_class = FirmwareForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.add_firmware"
    success_url = reverse_lazy("devices:firmware-list")
    raise_exception = True


class FirmwareUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = Firmware
    form_class = FirmwareForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.change_firmware"
    success_url = reverse_lazy("devices:firmware-list")
    raise_exception = True


class AdresseListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    ListView,
):
    model = Adresse
    template_name = "devices/adresse_list.html"
    context_object_name = "adressen"
    permission_required = "devices.view_adresse"
    raise_exception = True

    def get_queryset(self):
        queryset = Adresse.objects.all().order_by(
            "ort",
            "strasse",
            "hausnummer",
        )
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(strasse__icontains=search_query)
                | Q(plz__icontains=search_query)
                | Q(ort__icontains=search_query)
            )

        return queryset


class AdresseCreateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    model = Adresse
    form_class = AdresseForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.add_adresse"
    success_url = reverse_lazy("devices:adresse-list")
    raise_exception = True


class AdresseUpdateView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    model = Adresse
    form_class = AdresseForm
    template_name = "devices/stammdaten_form.html"
    permission_required = "devices.change_adresse"
    success_url = reverse_lazy("devices:adresse-list")
    raise_exception = True
