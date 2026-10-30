from django.contrib import admin
from django.urls import path
from dealerships import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("djangoapp/login", views.login_view, name="login"),
    path("djangoapp/logout", views.logout_view, name="logout"),
    path("djangoapp/register", views.register_view, name="register"),
    path("djangoapp/get_cars", views.get_cars, name="get_cars"),
    path("fetchDealers", views.fetch_dealers, name="fetch_dealers"),
    path("fetchDealers/<str:state>", views.fetch_dealers_by_state, name="fetch_dealers_by_state"),
    path("fetchDealer/<int:dealer_id>", views.fetch_dealer, name="fetch_dealer"),
    path("fetchReviews/dealer/<int:dealer_id>", views.fetch_reviews, name="fetch_reviews"),
    path("analyze/<path:review_text>", views.analyze_review, name="analyze_review"),
    path("about/", views.about_page, name="about"),
    path("contact/", views.contact_page, name="contact"),
]
