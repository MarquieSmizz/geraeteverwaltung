from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse


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
