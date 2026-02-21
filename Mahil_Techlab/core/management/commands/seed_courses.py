from django.core.management.base import BaseCommand

from core.models import Course


COURSES = [
    {
        "title": "Full Stack Web Development Bootcamp",
        "slug": "full-stack-web-development-bootcamp",
        "description": (
            "Build production-grade applications with HTML, CSS, JavaScript, Django, APIs, "
            "and deployment workflows."
        ),
        "duration_weeks": 16,
        "level": "Beginner",
        "fee_usd": "699.00",
    },
    {
        "title": "Python for Data and Automation",
        "slug": "python-for-data-and-automation",
        "description": (
            "Learn Python programming, automation scripts, data analysis basics, and practical "
            "workflow optimization."
        ),
        "duration_weeks": 10,
        "level": "Beginner",
        "fee_usd": "449.00",
    },
    {
        "title": "Cloud and DevOps Essentials",
        "slug": "cloud-and-devops-essentials",
        "description": (
            "Understand cloud infrastructure, CI/CD, Docker fundamentals, and deployment "
            "practices used in modern teams."
        ),
        "duration_weeks": 12,
        "level": "Intermediate",
        "fee_usd": "599.00",
    },
]


class Command(BaseCommand):
    help = "Seed initial courses for Mahil Techlab."

    def handle(self, *args, **options):
        created = 0
        updated = 0

        for payload in COURSES:
            _, was_created = Course.objects.update_or_create(
                slug=payload["slug"],
                defaults=payload,
            )
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Course seed complete. Created: {created}, Updated: {updated}"
            )
        )
