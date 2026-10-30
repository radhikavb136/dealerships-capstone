from django.contrib import admin
from .models import Dealer, Review

@admin.register(Dealer)
class DealerAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "city", "state", "zip")
    list_filter = ("state",)
    search_fields = ("full_name", "city", "state", "short_name")

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "dealership", "car_make", "car_model", "sentiment")
    list_filter = ("sentiment", "purchase", "car_make")
    search_fields = ("name", "review", "dealership__full_name")
