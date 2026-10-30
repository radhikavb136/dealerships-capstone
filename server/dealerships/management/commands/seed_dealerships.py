from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from dealerships.models import Dealer

# Ten realistic demo locations, repeated across five distinct dealer brands = 50 records.
LOCATIONS = [
    ("Wichita", "Kansas", "67202", 37.6872, -97.3301, "KS Auto Mall", "1200 E Kellogg Dr"),
    ("Overland Park", "Kansas", "66204", 38.9822, -94.6708, "Overland Motors", "8400 W 95th St"),
    ("Austin", "Texas", "78701", 30.2672, -97.7431, "Capital City Auto", "500 Congress Ave"),
    ("Dallas", "Texas", "75201", 32.7767, -96.7970, "Lone Star Motors", "1600 Main St"),
    ("Phoenix", "Arizona", "85004", 33.4484, -112.0740, "Desert Ridge Auto", "700 N Central Ave"),
    ("Denver", "Colorado", "80202", 39.7392, -104.9903, "Front Range Motors", "1550 Market St"),
    ("Seattle", "Washington", "98101", 47.6062, -122.3321, "Emerald City Auto", "900 Fourth Ave"),
    ("Miami", "Florida", "33130", 25.7617, -80.1918, "Sunshine Motors", "100 SW 8th St"),
    ("Columbus", "Ohio", "43215", 39.9612, -82.9988, "Buckeye Auto Group", "250 S High St"),
    ("Raleigh", "North Carolina", "27601", 35.7796, -78.6382, "Oak City Motors", "300 Fayetteville St"),
]
BRANDS = ["Premier", "Community", "Liberty", "Evergreen", "Summit"]

class Command(BaseCommand):
    help = "Create 50 deterministic demo dealership records across multiple US states."

    def handle(self, *args, **options):
        created = 0
        for location in LOCATIONS:
            city, state, zipcode, lat, lon, short, address = location
            for index, brand in enumerate(BRANDS, start=1):
                full_name = f"{brand} {short}"
                dealer, was_created = Dealer.objects.get_or_create(
                    full_name=full_name,
                    defaults={
                        "city": city, "state": state, "address": f"{address}, {city}, {state}",
                        "zip": zipcode, "lat": lat + index * 0.001, "long": lon - index * 0.001,
                        "short_name": f"{brand} {short}",
                    },
                )
                created += int(was_created)
        # Convenience account for local coursework only; change/remove before deployment.
        if not User.objects.filter(username="admin").exists():
            User.objects.create_user(username="admin", password="password", first_name="Demo", last_name="Admin", email="admin@example.test")
        self.stdout.write(self.style.SUCCESS(
            f"Seed complete: {Dealer.objects.count()} dealerships total ({created} newly created)."
        ))
