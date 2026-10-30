import json
from datetime import date
from urllib.parse import unquote

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Dealer, Review

CAR_MODELS = [
    {"make": "Toyota", "models": ["Camry", "Corolla", "RAV4", "Prius"]},
    {"make": "Honda", "models": ["Accord", "Civic", "CR-V", "Pilot"]},
    {"make": "Ford", "models": ["F-150", "Escape", "Explorer", "Mustang"]},
    {"make": "Chevrolet", "models": ["Malibu", "Equinox", "Silverado", "Tahoe"]},
    {"make": "Nissan", "models": ["Altima", "Sentra", "Rogue", "Pathfinder"]},
    {"make": "Hyundai", "models": ["Elantra", "Sonata", "Tucson", "Santa Fe"]},
    {"make": "Subaru", "models": ["Impreza", "Legacy", "Forester", "Outback"]},
    {"make": "Tesla", "models": ["Model 3", "Model S", "Model X", "Model Y"]},
]
POSITIVE_WORDS = {"fantastic", "excellent", "great", "helpful", "friendly", "wonderful", "love", "smooth", "recommend", "good", "amazing"}
NEGATIVE_WORDS = {"terrible", "awful", "bad", "rude", "poor", "horrible", "hate", "slow", "disappointed", "worst"}

def json_body(request):
    try:
        return json.loads(request.body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Request body must be valid JSON.") from None

def dealer_json(dealer):
    return {
        "id": dealer.id, "city": dealer.city, "state": dealer.state,
        "address": dealer.address, "zip": dealer.zip, "lat": dealer.lat,
        "long": dealer.long, "short_name": dealer.short_name, "full_name": dealer.full_name,
    }

def sentiment_for(text):
    words = {word.lower().strip(".,!?;:()[]{}") for word in text.split()}
    score = len(words & POSITIVE_WORDS) - len(words & NEGATIVE_WORDS)
    return "positive" if score > 0 else "negative" if score < 0 else "neutral"

@csrf_exempt
@require_POST
def login_view(request):
    try:
        data = json_body(request)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    username = str(data.get("userName", "")).strip()
    password = str(data.get("password", ""))
    if not username or not password:
        return JsonResponse({"error": "userName and password are required."}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"userName": "", "error": "Invalid username or password."}, status=401)
    login(request, user)
    return JsonResponse({"userName": user.username, "status": "Authenticated"})

@require_GET
def logout_view(request):
    logout(request)
    return JsonResponse({"userName": ""})

@csrf_exempt
@require_POST
def register_view(request):
    try:
        data = json_body(request)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    username = str(data.get("userName", data.get("username", ""))).strip()
    first_name = str(data.get("firstName", "")).strip()
    last_name = str(data.get("lastName", "")).strip()
    email = str(data.get("email", "")).strip()
    password = str(data.get("password", ""))
    if not all([username, first_name, last_name, email, password]):
        return JsonResponse({"error": "All five fields are required."}, status=400)
    if len(password) < 8:
        return JsonResponse({"error": "Password must be at least 8 characters."}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({"error": "Username already exists."}, status=409)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Email already exists."}, status=409)
    user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=password)
    return JsonResponse({"userName": user.username, "status": "Registered"}, status=201)

@require_GET
def fetch_dealers(request):
    return JsonResponse([dealer_json(d) for d in Dealer.objects.all()], safe=False)

@require_GET
def fetch_dealers_by_state(request, state):
    dealers = Dealer.objects.filter(state__iexact=state)
    return JsonResponse([dealer_json(d) for d in dealers], safe=False)

@require_GET
def fetch_dealer(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    return JsonResponse(dealer_json(dealer))

@csrf_exempt
@require_http_methods(["GET", "POST"])
def fetch_reviews(request, dealer_id):
    dealer = get_object_or_404(Dealer, pk=dealer_id)
    if request.method == "GET":
        reviews = Review.objects.filter(dealership=dealer).select_related("author")
        return JsonResponse([{
            "id": r.id, "name": r.name, "dealership": r.dealership_id,
            "review": r.review, "purchase": r.purchase,
            "purchase_date": r.purchase_date.isoformat() if r.purchase_date else None,
            "car_make": r.car_make, "car_model": r.car_model, "car_year": r.car_year,
            "sentiment": r.sentiment,
        } for r in reviews], safe=False)
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Please log in before submitting a review."}, status=401)
    try:
        data = json_body(request)
    except ValueError as exc:
        return JsonResponse({"error": str(exc)}, status=400)
    review_text = str(data.get("review", "")).strip()
    make = str(data.get("car_make", "")).strip()
    model = str(data.get("car_model", "")).strip()
    try:
        year = int(data.get("car_year"))
    except (TypeError, ValueError):
        return JsonResponse({"error": "car_year must be a valid year."}, status=400)
    if not review_text or not make or not model:
        return JsonResponse({"error": "review, car_make, and car_model are required."}, status=400)
    purchase_date = None
    if data.get("purchase_date"):
        try:
            purchase_date = date.fromisoformat(str(data["purchase_date"]))
        except ValueError:
            return JsonResponse({"error": "purchase_date must use YYYY-MM-DD."}, status=400)
    review = Review.objects.create(
        name=(request.user.get_full_name() or request.user.username),
        dealership=dealer, author=request.user, review=review_text,
        purchase=bool(data.get("purchase", False)), purchase_date=purchase_date,
        car_make=make, car_model=model, car_year=year, sentiment=sentiment_for(review_text),
    )
    return JsonResponse({
        "id": review.id, "name": review.name, "dealership": dealer.id,
        "review": review.review, "purchase": review.purchase,
        "purchase_date": review.purchase_date.isoformat() if review.purchase_date else None,
        "car_make": review.car_make, "car_model": review.car_model,
        "car_year": review.car_year, "sentiment": review.sentiment,
    }, status=201)

@require_GET
def get_cars(request):
    return JsonResponse({"CarModels": CAR_MODELS})

@require_GET
def analyze_review(request, review_text):
    text = unquote(review_text)
    return JsonResponse({"review": text, "sentiment": sentiment_for(text)})

def about_page(request):
    return render(request, "About.html")

def contact_page(request):
    return render(request, "Contact.html")
