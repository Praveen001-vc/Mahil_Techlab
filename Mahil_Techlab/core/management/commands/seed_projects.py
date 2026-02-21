from django.core.management.base import BaseCommand

from core.models import Project


PROJECTS = [
    {
        "name": "MahilMart POS",
        "slug": "mahilmart-pos",
        "icon_url": "",
        "tagline": "Desktop billing and inventory software for retail teams.",
        "short_description": (
            "MahilMart POS is a Windows desktop application for billing, stock handling, "
            "supplier workflows, and operational reporting."
        ),
        "details": (
            "Use MahilMart POS for day-to-day retail operations.\n\n"
            "Key modules:\n"
            "- Billing and returns\n"
            "- Product and inventory management\n"
            "- Supplier and purchase tracking\n"
            "- Reports and activity logs\n\n"
            "Install using the official setup package."
        ),
        "install_url": "",
        "version": "1.0.0",
        "is_active": True,
        "display_order": 1,
    }
]


class Command(BaseCommand):
    help = "Seed initial software projects for Mahil Techlab."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for payload in PROJECTS:
            _, was_created = Project.objects.update_or_create(
                slug=payload["slug"],
                defaults=payload,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Project seed complete. Created: {created}, Updated: {updated}"
            )
        )
