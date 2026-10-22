from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from .models import Adresse, DeviceType, Firmware


User = get_user_model()


@permission_required("devices.add_devicetype", raise_exception=True)
def protected_write_probe(request):
    return None


class AuthenticationAndAuthorizationTests(TestCase):
    test_password = "Lokaler-Test-123!"

    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)

        reader_group = Group.objects.get(name="Leser")
        editor_group = Group.objects.get(name="Bearbeiter")

        cls.reader = User.objects.create_user(
            username="test_leser",
            password=cls.test_password,
        )
        cls.editor = User.objects.create_user(
            username="test_bearbeiter",
            password=cls.test_password,
        )

        cls.reader.groups.add(reader_group)
        cls.editor.groups.add(editor_group)

    def test_valid_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_leser",
                "password": self.test_password,
            },
        )

        self.assertRedirects(response, reverse("home"))

    def test_invalid_login(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "test_leser",
                "password": "falsches-passwort",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Benutzername oder Passwort ist ungültig.",
        )

    def test_unauthenticated_access_redirects_to_login(self):
        response = self.client.get(reverse("home"))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={reverse('home')}",
        )

    def test_logout_requires_post_and_succeeds(self):
        self.client.force_login(self.reader)

        get_response = self.client.get(reverse("logout"))
        self.assertEqual(get_response.status_code, 405)

        post_response = self.client.post(reverse("logout"))
        self.assertRedirects(post_response, reverse("login"))

    def test_reader_has_only_read_permissions(self):
        for model_name in ("device", "devicetype", "firmware", "adresse"):
            self.assertTrue(
                self.reader.has_perm(f"devices.view_{model_name}")
            )

        for permission in (
            "add_devicetype",
            "change_devicetype",
            "delete_devicetype",
            "add_firmware",
            "change_firmware",
            "delete_firmware",
            "add_adresse",
            "change_adresse",
            "delete_adresse",
        ):
            self.assertFalse(self.reader.has_perm(f"devices.{permission}"))

    def test_editor_has_expected_write_permissions(self):
        for model_name in ("devicetype", "firmware", "adresse"):
            self.assertTrue(
                self.editor.has_perm(f"devices.add_{model_name}")
            )
            self.assertTrue(
                self.editor.has_perm(f"devices.change_{model_name}")
            )
            self.assertFalse(
                self.editor.has_perm(f"devices.delete_{model_name}")
            )

        for permission in (
            "add_device",
            "change_device",
            "delete_device",
        ):
            self.assertFalse(self.editor.has_perm(f"devices.{permission}"))

    def test_reader_is_denied_server_side_write_access(self):
        request = RequestFactory().get("/")
        request.user = self.reader

        with self.assertRaises(PermissionDenied):
            protected_write_probe(request)

    def test_editor_is_allowed_server_side_write_access(self):
        request = RequestFactory().get("/")
        request.user = self.editor

        self.assertIsNone(protected_write_probe(request))

class DeviceTypeListTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)

        reader_group = Group.objects.get(name="Leser")
        cls.reader = User.objects.create_user(
            username="list_leser",
            password="Lokaler-Test-123!",
        )
        cls.reader.groups.add(reader_group)

        cls.device_type = DeviceType.objects.create(
            hersteller="TestMeter",
            klasse="Smart Meter",
            modell="SM-100",
            typnummer="SM-100-DE",
            beschreibung="Synthetischer Testdatensatz",
        )

    def test_device_type_list_displays_existing_record(self):
        self.client.force_login(self.reader)

        response = self.client.get(reverse("devices:devicetype-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestMeter")
        self.assertContains(response, "SM-100")

    def test_device_type_search_filters_records(self):
        DeviceType.objects.create(
            hersteller="OtherMeter",
            klasse="Smart Meter",
            modell="OM-200",
            typnummer="OM-200-DE",
        )
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("devices:devicetype-list"),
            {"q": "TestMeter"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestMeter")
        self.assertNotContains(response, "OtherMeter")

class DeviceTypeWriteTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)

        reader_group = Group.objects.get(name="Leser")
        editor_group = Group.objects.get(name="Bearbeiter")

        cls.reader = User.objects.create_user(
            username="write_leser",
            password="Lokaler-Test-123!",
        )
        cls.editor = User.objects.create_user(
            username="write_bearbeiter",
            password="Lokaler-Test-123!",
        )

        cls.reader.groups.add(reader_group)
        cls.editor.groups.add(editor_group)

        cls.device_type = DeviceType.objects.create(
            hersteller="EditMeter",
            klasse="Smart Meter",
            modell="EM-100",
            typnummer="EM-100-DE",
        )

    def test_editor_can_create_device_type(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("devices:devicetype-create"),
            {
                "hersteller": "NewMeter",
                "klasse": "Smart Meter",
                "modell": "NM-200",
                "typnummer": "NM-200-DE",
                "beschreibung": "Testanlage",
            },
        )

        self.assertRedirects(
            response,
            reverse("devices:devicetype-list"),
        )
        self.assertTrue(
            DeviceType.objects.filter(
                hersteller="NewMeter",
                typnummer="NM-200-DE",
            ).exists()
        )

    def test_editor_can_update_device_type(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
                "devices:devicetype-update",
                args=[self.device_type.pk],
            ),
            {
                "hersteller": "EditMeter",
                "klasse": "Smart Meter",
                "modell": "EM-100X",
                "typnummer": "EM-100-DE",
                "beschreibung": "",
            },
        )

        self.assertRedirects(
            response,
            reverse("devices:devicetype-list"),
        )
        self.device_type.refresh_from_db()
        self.assertEqual(self.device_type.modell, "EM-100X")

    def test_reader_cannot_create_device_type(self):
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("devices:devicetype-create")
        )

        self.assertEqual(response.status_code, 403)

    def test_reader_cannot_update_device_type(self):
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse(
                "devices:devicetype-update",
                args=[self.device_type.pk],
            )
        )

        self.assertEqual(response.status_code, 403)

class FirmwareManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)

        reader_group = Group.objects.get(name="Leser")
        editor_group = Group.objects.get(name="Bearbeiter")

        cls.reader = User.objects.create_user(
            username="firmware_leser",
            password="Lokaler-Test-123!",
        )
        cls.editor = User.objects.create_user(
            username="firmware_bearbeiter",
            password="Lokaler-Test-123!",
        )

        cls.reader.groups.add(reader_group)
        cls.editor.groups.add(editor_group)

        cls.firmware = Firmware.objects.create(
            firmware_name="TestFirmware",
            version="1.0.0",
        )

    def test_firmware_list_displays_existing_record(self):
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("devices:firmware-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestFirmware")
        self.assertContains(response, "1.0.0")

    def test_firmware_search_filters_records(self):
        Firmware.objects.create(
            firmware_name="OtherFirmware",
            version="2.0.0",
        )
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("devices:firmware-list"),
            {"q": "TestFirmware"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestFirmware")
        self.assertNotContains(response, "OtherFirmware")

    def test_editor_can_create_firmware(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("devices:firmware-create"),
            {
                "firmware_name": "NewFirmware",
                "version": "3.0.0",
            },
        )

        self.assertRedirects(
            response,
            reverse("devices:firmware-list"),
        )
        self.assertTrue(
            Firmware.objects.filter(
                firmware_name="NewFirmware",
                version="3.0.0",
            ).exists()
        )

    def test_editor_can_update_firmware(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse(
                "devices:firmware-update",
                args=[self.firmware.pk],
            ),
            {
                "firmware_name": "TestFirmware",
                "version": "1.1.0",
            },
        )

        self.assertRedirects(
            response,
            reverse("devices:firmware-list"),
        )
        self.firmware.refresh_from_db()
        self.assertEqual(self.firmware.version, "1.1.0")

    def test_reader_cannot_write_firmware(self):
        self.client.force_login(self.reader)

        create_response = self.client.get(
            reverse("devices:firmware-create")
        )
        update_response = self.client.get(
            reverse(
                "devices:firmware-update",
                args=[self.firmware.pk],
            )
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

class AddressManagementTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_roles", verbosity=0)

        reader_group = Group.objects.get(name="Leser")
        editor_group = Group.objects.get(name="Bearbeiter")

        cls.reader = User.objects.create_user(
            username="adresse_leser",
            password="Lokaler-Test-123!",
        )
        cls.editor = User.objects.create_user(
            username="adresse_bearbeiter",
            password="Lokaler-Test-123!",
        )

        cls.reader.groups.add(reader_group)
        cls.editor.groups.add(editor_group)

        cls.address = Adresse.objects.create(
            strasse="Teststraße",
            hausnummer="1",
            plz="60311",
            ort="Frankfurt am Main",
            land="Deutschland",
        )

    def test_address_list_and_search(self):
        Adresse.objects.create(
            strasse="Andere Straße",
            hausnummer="2",
            plz="70173",
            ort="Stuttgart",
            land="Deutschland",
        )
        self.client.force_login(self.reader)

        response = self.client.get(
            reverse("devices:adresse-list"),
            {"q": "Frankfurt"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Teststraße")
        self.assertNotContains(response, "Andere Straße")

    def test_editor_can_create_and_update_address(self):
        self.client.force_login(self.editor)

        create_response = self.client.post(
            reverse("devices:adresse-create"),
            {
                "strasse": "Neue Straße",
                "hausnummer": "10",
                "plz": "20095",
                "ort": "Hamburg",
                "land": "Deutschland",
            },
        )

        self.assertRedirects(
            create_response,
            reverse("devices:adresse-list"),
        )

        created_address = Adresse.objects.get(strasse="Neue Straße")

        update_response = self.client.post(
            reverse(
                "devices:adresse-update",
                args=[created_address.pk],
            ),
            {
                "strasse": "Geänderte Straße",
                "hausnummer": "10",
                "plz": "20095",
                "ort": "Hamburg",
                "land": "Deutschland",
            },
        )

        self.assertRedirects(
            update_response,
            reverse("devices:adresse-list"),
        )
        created_address.refresh_from_db()
        self.assertEqual(created_address.strasse, "Geänderte Straße")

    def test_reader_cannot_write_address(self):
        self.client.force_login(self.reader)

        create_response = self.client.get(
            reverse("devices:adresse-create")
        )
        update_response = self.client.get(
            reverse(
                "devices:adresse-update",
                args=[self.address.pk],
            )
        )

        self.assertEqual(create_response.status_code, 403)
        self.assertEqual(update_response.status_code, 403)

    def test_invalid_german_postcode_is_rejected(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("devices:adresse-create"),
            {
                "strasse": "Ungültige Straße",
                "hausnummer": "5",
                "plz": "1234",
                "ort": "Berlin",
                "land": "Deutschland",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Bitte geben Sie eine gültige fünfstellige Postleitzahl ein.",
        )
        self.assertFalse(
            Adresse.objects.filter(strasse="Ungültige Straße").exists()
        )

    def test_required_address_field_is_rejected(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("devices:adresse-create"),
            {
                "strasse": "",
                "hausnummer": "5",
                "plz": "10115",
                "ort": "Berlin",
                "land": "Deutschland",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Adresse.objects.filter(hausnummer="5", ort="Berlin").exists()
        )

    def test_duplicate_address_is_rejected(self):
        self.client.force_login(self.editor)

        response = self.client.post(
            reverse("devices:adresse-create"),
            {
                "strasse": "Teststraße",
                "hausnummer": "1",
                "plz": "60311",
                "ort": "Frankfurt am Main",
                "land": "Deutschland",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            Adresse.objects.filter(
                strasse="Teststraße",
                hausnummer="1",
                plz="60311",
                ort="Frankfurt am Main",
                land="Deutschland",
            ).count(),
            1,
        )
