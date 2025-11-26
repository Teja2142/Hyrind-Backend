Admin Dashboard & Logging

- Dashboard URL: /admin/dashboard/ (requires superuser)
- The admin site has a lightweight dashboard showing counts for:
  - Onboarded users
  - Active subscriptions
  - Assignments

Toggling request-level audit logging

- To disable request-level audit logging, set `AUDIT_LOG_REQUESTS = False` in `hyrind/settings.py`.
- By default it is enabled for development convenience. In production you may want to disable it to avoid noisy logs and storage growth.

AuditLog

- Audit logs are written to the `audit_auditlog` table and viewable via Django admin.
- Key events logged: user registration, onboarding completion, subscription creation, recruiter assignment, and HTTP requests (if enabled).

Migrations

Run:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Create a superuser:

```powershell
python manage.py createsuperuser
```

Access admin:

```powershell
# Run development server
python manage.py runserver
# Open http://127.0.0.1:8000/admin/dashboard/
```
