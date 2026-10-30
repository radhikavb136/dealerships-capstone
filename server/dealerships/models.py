from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

class Dealer(models.Model):
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=80, db_index=True)
    address = models.CharField(max_length=200)
    zip = models.CharField(max_length=10)
    lat = models.FloatField()
    long = models.FloatField()
    short_name = models.CharField(max_length=120)
    full_name = models.CharField(max_length=200)

    class Meta:
        ordering = ["state", "city", "full_name"]

    def __str__(self):
        return self.full_name

class Review(models.Model):
    name = models.CharField(max_length=150)
    dealership = models.ForeignKey(Dealer, related_name="reviews", on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dealer_reviews", on_delete=models.CASCADE)
    review = models.TextField(max_length=3000)
    purchase = models.BooleanField(default=False)
    purchase_date = models.DateField(null=True, blank=True)
    car_make = models.CharField(max_length=80)
    car_model = models.CharField(max_length=80)
    car_year = models.PositiveIntegerField(validators=[MinValueValidator(1900), MaxValueValidator(2100)])
    sentiment = models.CharField(max_length=10, default="neutral")

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.dealership.short_name} review by {self.name}"
