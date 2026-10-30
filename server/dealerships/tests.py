import json
from django.contrib.auth.models import User
from django.test import TestCase
from .models import Dealer, Review

class DealershipApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.dealer = Dealer.objects.create(
            city="Wichita", state="Kansas", address="100 Main St", zip="67202",
            lat=37.68, long=-97.33, short_name="Test Auto", full_name="Test Auto Wichita",
        )
        cls.user = User.objects.create_user(username="admin", password="password123", first_name="Demo")

    def test_login_logout(self):
        response = self.client.post("/djangoapp/login", data=json.dumps({
            "userName": "admin", "password": "password123",
        }), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Authenticated")
        self.assertEqual(self.client.get("/djangoapp/logout").json()["userName"], "")

    def test_dealer_list_filter_and_detail(self):
        self.assertEqual(len(self.client.get("/fetchDealers").json()), 1)
        self.assertEqual(len(self.client.get("/fetchDealers/Kansas").json()), 1)
        self.assertEqual(self.client.get(f"/fetchDealer/{self.dealer.id}").json()["full_name"], "Test Auto Wichita")

    def test_cars_and_sentiment(self):
        self.assertTrue(self.client.get("/djangoapp/get_cars").json()["CarModels"])
        response = self.client.get("/analyze/Fantastic%20services")
        self.assertEqual(response.json()["sentiment"], "positive")

    def test_review_submit_and_retrieve(self):
        self.client.force_login(self.user)
        response = self.client.post(
            f"/fetchReviews/dealer/{self.dealer.id}",
            data=json.dumps({
                "review": "Fantastic services", "purchase": True, "purchase_date": "2025-06-12",
                "car_make": "Toyota", "car_model": "Camry", "car_year": 2024,
            }), content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["sentiment"], "positive")
        self.assertEqual(len(self.client.get(f"/fetchReviews/dealer/{self.dealer.id}").json()), 1)
