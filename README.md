# Event Management Platform

A Django event-management application for discovering events and venues, registering for events, coordinating through role-based dashboards, and recording payments. The project is a server-rendered monolith with Django REST Framework endpoints and a Channels WebSocket path for advanced chat.

## What is implemented

- Custom email-based user authentication with role-aware user, manager, vendor, and administrator workflows.
- Event creation, category browsing, registration, galleries, reviews, and event dashboards.
- Venue discovery, detail pages, galleries, availability, booking, and reviews.
- REST endpoints grouped under `/api/` for the domain applications.
- Conversation and chat-room views, plus an authenticated WebSocket route at `ws/advanced-chat/<room_id>/`.
- Invoices, payment records, refunds, Stripe webhook handling, and a development payment mode that simulates successful payments.
- Rule-based chatbot responses that read event and venue data. The chatbot page is present, but this repository does not contain an OpenAI model integration.
- Analytics and administrative dashboards, email templates, media uploads, and PDF invoice/report generation.

## Stack

- Python 3.8+ and Django 4.2
- Django REST Framework, django-allauth, django-axes, django-otp, and django-ckeditor-5
- Django Channels with an in-memory channel layer in the checked-in settings
- SQLite by default; MySQL is selected with `USE_MYSQL=True`
- Server-rendered Django templates, CSS, and JavaScript
- Stripe integration with safe development defaults

Optional packages in `requirements.txt` support deployment and integrations that are not enabled by default in the current settings, including Celery, Redis, S3 storage, PostgreSQL, and malware-scanning tooling.

## Local setup

### Prerequisites

- Python 3.8 or newer
- A virtual environment
- SQLite for the default local configuration

### Install and run

```bash
git clone https://github.com/Meet-1409/Event-Management-Platform.git
cd Event-Management-Platform
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and create a local environment file:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env  # Windows PowerShell
# cp .env.example .env  # macOS/Linux
```

For a local run, the defaults in `.env.example` are sufficient. Replace `SECRET_KEY`, set `DEBUG=False`, configure `ALLOWED_HOSTS`, and provide real email/payment values before deployment.

```bash
python manage.py migrate
python manage.py check
python manage.py createsuperuser
python manage.py runserver
```

Open `http://127.0.0.1:8000/`. Development settings use the console email backend and mock payments unless a live Stripe key is configured.

## Configuration

The application reads settings with `python-decouple`. The supported variables and their defaults are documented in `.env.example`, including:

- `SECRET_KEY`, `DEBUG`, and `ALLOWED_HOSTS`
- MySQL connection values enabled by `USE_MYSQL`
- SMTP settings for non-debug mode
- Stripe keys and webhook secret
- `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, and `CSRF_COOKIE_SECURE`
- Celery and CORS settings retained for optional integrations

Never commit `.env` or real credentials. The default development key and Stripe placeholders are deliberately non-production values.

## Testing

Run the Django test suite with:

```bash
python manage.py test
```

The maintained tests live in `tests/` and cover smoke workflows, links and URL names, and theme visibility. See [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md) for the current validation snapshot and known gaps.

## Project documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md): repository map and ownership boundaries
- [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md): architecture, runtime behavior, security posture, and limitations
- [CONTRIBUTING.md](CONTRIBUTING.md): development and pull request workflow

## License

This project is available under the [MIT License](LICENSE).