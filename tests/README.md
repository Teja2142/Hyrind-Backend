Happy-path test

- Start the dev server: `python manage.py runserver`
- Run this test script (requires `requests`):

```powershell
python tests/happy_path.py
```

Notes:
- The script assumes profile ID 1 will be created for the registered user. If not, adjust the profile IDs.
- The script skips admin-only recruiter assignment step (requires admin token).
