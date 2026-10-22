from django import forms

from .models import Adresse, DeviceType, Firmware


class DeviceTypeForm(forms.ModelForm):
    class Meta:
        model = DeviceType
        fields = [
            "hersteller",
            "klasse",
            "modell",
            "typnummer",
            "beschreibung",
        ]
        labels = {
            "hersteller": "Hersteller",
            "klasse": "Klasse",
            "modell": "Modell",
            "typnummer": "Typnummer",
            "beschreibung": "Beschreibung",
        }
        widgets = {
            "beschreibung": forms.Textarea(attrs={"rows": 4}),
        }


class FirmwareForm(forms.ModelForm):
    class Meta:
        model = Firmware
        fields = [
            "firmware_name",
            "version",
        ]
        labels = {
            "firmware_name": "Firmwarebezeichnung",
            "version": "Version",
        }


class AdresseForm(forms.ModelForm):
    class Meta:
        model = Adresse
        fields = [
            "strasse",
            "hausnummer",
            "plz",
            "ort",
            "land",
        ]
        labels = {
            "strasse": "Straße",
            "hausnummer": "Hausnummer",
            "plz": "Postleitzahl",
            "ort": "Ort",
            "land": "Land",
        }
