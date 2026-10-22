from django.core.validators import RegexValidator
from django.db import models


class DeviceType(models.Model):
    device_type_id = models.AutoField(primary_key=True)
    hersteller = models.CharField(max_length=100)
    klasse = models.CharField(max_length=100)
    modell = models.CharField(max_length=100)
    typnummer = models.CharField(max_length=50)
    beschreibung = models.TextField(blank=True)

    class Meta:
        db_table = "device_types"
        constraints = [
            models.UniqueConstraint(
                fields=["hersteller", "klasse", "modell"],
                name="uq_device_type_manufacturer_class_model",
            ),
            models.UniqueConstraint(
                fields=["hersteller", "typnummer"],
                name="uq_device_type_manufacturer_number",
            ),
        ]

    def __str__(self):
        return f"{self.hersteller} {self.modell} ({self.typnummer})"


class Firmware(models.Model):
    firmware_id = models.AutoField(primary_key=True)
    firmware_name = models.CharField(max_length=100)
    version = models.CharField(max_length=50)

    class Meta:
        db_table = "firmwares"
        constraints = [
            models.UniqueConstraint(
                fields=["firmware_name", "version"],
                name="uq_firmware_name_version",
            ),
        ]

    def __str__(self):
        return f"{self.firmware_name} {self.version}"


class Adresse(models.Model):
    adresse_id = models.AutoField(primary_key=True)
    strasse = models.CharField(max_length=100)
    hausnummer = models.CharField(max_length=20)
    plz = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{5}$",
                message="Bitte geben Sie eine gültige fünfstellige Postleitzahl ein.",
            )
        ],
    )
    ort = models.CharField(max_length=100)
    land = models.CharField(max_length=100, default="Deutschland")

    class Meta:
        db_table = "adressen"
        constraints = [
            models.UniqueConstraint(
                fields=["strasse", "hausnummer", "plz", "ort", "land"],
                name="uq_address_full_address",
            ),
        ]

    def __str__(self):
        return f"{self.strasse} {self.hausnummer}, {self.plz} {self.ort}"


class Device(models.Model):
    device_id = models.AutoField(primary_key=True)
    seriennummer = models.CharField(max_length=100, unique=True)
    device_type = models.ForeignKey(
        DeviceType,
        on_delete=models.PROTECT,
        db_column="device_type_id",
    )
    firmware = models.ForeignKey(
        Firmware,
        on_delete=models.PROTECT,
        db_column="firmware_id",
    )
    adresse = models.ForeignKey(
        Adresse,
        on_delete=models.PROTECT,
        db_column="adresse_id",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "devices"

    def __str__(self):
        return self.seriennummer
