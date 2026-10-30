from django.conf import settings
from django.db import migrations, models
import django.core.validators
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="Dealer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("city", models.CharField(max_length=100)),
                ("state", models.CharField(db_index=True, max_length=80)),
                ("address", models.CharField(max_length=200)),
                ("zip", models.CharField(max_length=10)),
                ("lat", models.FloatField()),
                ("long", models.FloatField()),
                ("short_name", models.CharField(max_length=120)),
                ("full_name", models.CharField(max_length=200)),
            ],
            options={"ordering": ["state", "city", "full_name"]},
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("review", models.TextField(max_length=3000)),
                ("purchase", models.BooleanField(default=False)),
                ("purchase_date", models.DateField(blank=True, null=True)),
                ("car_make", models.CharField(max_length=80)),
                ("car_model", models.CharField(max_length=80)),
                ("car_year", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2100)])),
                ("sentiment", models.CharField(default="neutral", max_length=10)),
                ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="dealer_reviews", to=settings.AUTH_USER_MODEL)),
                ("dealership", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="dealerships.dealer")),
            ],
            options={"ordering": ["-id"]},
        ),
    ]
