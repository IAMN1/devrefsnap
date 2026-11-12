from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Book


class BookAdminTests(TestCase):
    def test_anonymous_visitor_is_redirected_to_admin_login(self):
        add_url = reverse("admin:catalog_book_add")
        login_url = reverse("admin:login")

        response = self.client.get(add_url)

        self.assertRedirects(response, f"{login_url}?next={add_url}")

    def test_superuser_can_add_book(self):
        admin_user = get_user_model().objects.create_superuser(username="admin")
        self.client.force_login(admin_user)

        response = self.client.post(
            reverse("admin:catalog_book_add"), {"title": "Demo Book"}
        )

        self.assertRedirects(response, reverse("admin:catalog_book_changelist"))
        self.assertTrue(Book.objects.filter(title="Demo Book").exists())
