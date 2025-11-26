# Hyrind-Backend

This repository contains a starter Django backend for Hyrind — a platform where users can register, post/accept jobs, and pay for services.

What's included:
- Django project scaffold (`hyrind`)
- Apps: `users`, `jobs`, `payments`
- REST API basics with Django REST Framework

Quick start (Windows PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Notes:
- Payments endpoint is a placeholder — integrate Stripe (keys via env vars) for production.
- This is a minimal scaffold to get started. Next steps: authentication (JWT), tests, CI, and more detailed models.
# Hyrind-Backend