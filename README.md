# Dealerships Capstone — Dealership Management & Reviews

A beginner-friendly Django REST-style JSON API and React/Vite website for browsing US dealerships, viewing/submitting customer reviews, registering, signing in, and checking demo sentiment analysis.

## Features
- Django + SQLite models for dealerships and reviews
- Seed command creates 50 deterministic demo dealerships across US states
- Session-based login/logout and registration
- JSON endpoints for dealerships, reviews, car makes/models, and sentiment
- Django admin
- Responsive React UI with state filter, dealer details, reviews, review form, login/register, About and Contact pages
- GitHub Actions with separate Python and JavaScript lint jobs
- Local-first configuration; deployment notes included

> Demo notes: sentiment is a lightweight keyword-based demo, not an ML model. The sample dataset is synthetic demo data. Use HTTPS, secure cookies, production secrets, a real sentiment model, rate limiting, and a production database before public deployment.

## Folder structure
```text
dealerships-capstone/
├── .github/workflows/lint.yml
├── server/
│   ├── manage.py
│   ├── requirements.txt
│   ├── pyproject.toml
│   ├── config/
│   ├── dealerships/
│   └── frontend/
│       ├── static/About.html
│       ├── static/Contact.html
│       ├── static/css/site.css
│       └── src/components/Register/Register.jsx
└── client/
    ├── package.json
    ├── index.html
    └── src/
```

## Requirements
- Python 3.11 or 3.12
- Node.js 20+ and npm
- Git (optional for local use)

## Windows setup (PowerShell)
1. Extract `dealerships-capstone.zip`.
2. Open the extracted `dealerships-capstone` folder in VS Code (`File → Open Folder`).
3. Open a terminal in VS Code.

### Backend
```powershell
cd server
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_dealerships
python manage.py createsuperuser
python manage.py runserver
```
If `py -3.12` is unavailable, use `py -3.11` or `python -m venv .venv`. If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again. Backend runs at `http://127.0.0.1:8000`.

Demo login after seeding: username `admin`, password `password` (local coursework convenience account only). Admin: open `http://127.0.0.1:8000/admin/` and use the superuser you created. Do not use the demo credentials on a public deployment.

### Frontend (new terminal)
```powershell
cd client
npm install
npm run dev
```
Open the URL Vite prints (normally `http://localhost:5173`). The frontend proxies API requests to Django.

### Tests and lint
Backend terminal, from `server`:
```powershell
python manage.py test
ruff check .
```
Frontend terminal, from `client`:
```powershell
npm run lint
npm run build
```

## API documentation
All paths below are relative to the local backend origin `http://127.0.0.1:8000`.

| Method | Path | Purpose |
|---|---|---|
| POST | `/djangoapp/login` | Accepts JSON `{ "userName": "...", "password": "..." }`; returns `userName` and `status: "Authenticated"` on success |
| GET | `/djangoapp/logout` | Ends the session and returns an empty `userName` |
| POST | `/djangoapp/register` | Creates a user from username, first/last name, email, password |
| GET | `/fetchDealers` | Lists all dealership records |
| GET | `/fetchDealers/<state>` | Filters dealerships by full state name (case-insensitive) |
| GET | `/fetchDealer/<dealer_id>` | Gets one dealership |
| GET | `/fetchReviews/dealer/<dealer_id>` | Lists reviews; POST to same route creates a review for authenticated users |
| GET | `/djangoapp/get_cars` | Returns `CarModels` array |
| GET | `/analyze/<review_text>` | Returns JSON sentiment; URL-encode review text |

Review POST JSON example:
```json
{
  "review": "Fantastic services",
  "purchase": true,
  "purchase_date": "2025-06-12",
  "car_make": "Toyota",
  "car_model": "Camry",
  "car_year": 2024
}
```
Login first in the same browser/session. Review author is taken from the authenticated session.

## GitHub Actions
Push the folder to a GitHub repository. The workflow `.github/workflows/lint.yml` runs independent Python lint and JavaScript lint jobs. Python job installs `server/requirements.txt` and runs Ruff; JavaScript job installs npm dependencies and runs ESLint. GitHub Actions results are only generated after you push and the workflow runs; no logs are claimed here.

## Deployment notes
This project is configured for local development, not deployed. For a deployment, choose a host that supports Django and a persistent database, set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False`, configure `DJANGO_ALLOWED_HOSTS`, serve static assets with a production static-file strategy, run migrations and the seed command only if demo data is desired, and use HTTPS. Configure the frontend API proxy/base URL for the chosen backend origin. No deployment URL is supplied because the app has not been deployed.
