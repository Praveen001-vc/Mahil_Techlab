from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_homeslider"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="github_url",
            field=models.URLField(blank=True),
        ),
    ]
