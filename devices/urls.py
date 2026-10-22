from django.urls import path

from .views import (
    AdresseCreateView,
    AdresseListView,
    AdresseUpdateView,
    DeviceTypeCreateView,
    DeviceTypeListView,
    DeviceTypeUpdateView,
    FirmwareCreateView,
    FirmwareListView,
    FirmwareUpdateView,
)

app_name = "devices"

urlpatterns = [
    path(
        "device-types/",
        DeviceTypeListView.as_view(),
        name="devicetype-list",
    ),
    path(
        "device-types/new/",
        DeviceTypeCreateView.as_view(),
        name="devicetype-create",
    ),
    path(
        "device-types/<int:pk>/edit/",
        DeviceTypeUpdateView.as_view(),
        name="devicetype-update",
    ),
    path(
        "firmwares/",
        FirmwareListView.as_view(),
        name="firmware-list",
    ),
    path(
        "firmwares/new/",
        FirmwareCreateView.as_view(),
        name="firmware-create",
    ),
    path(
        "firmwares/<int:pk>/edit/",
        FirmwareUpdateView.as_view(),
        name="firmware-update",
    ),
    path(
        "adressen/",
        AdresseListView.as_view(),
        name="adresse-list",
    ),
    path(
        "adressen/new/",
        AdresseCreateView.as_view(),
        name="adresse-create",
    ),
    path(
        "adressen/<int:pk>/edit/",
        AdresseUpdateView.as_view(),
        name="adresse-update",
    ),
]
