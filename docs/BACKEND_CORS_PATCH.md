# Backend CORS patch for the deployed frontend

This is a deployment prerequisite, not a change applied in the `frontend`
branch. The checked-in Django settings have no CORS middleware or
allowed-origin configuration. Apply the following minimal changes on the
`django-backend` branch, verify them, and deploy that backend branch before
expecting a Vercel-hosted browser app to call Render directly.

## 1. Add the dependency

In `backend/Pipfile` add:

```toml
django-cors-headers = "*"
```

Then regenerate and commit the lock file on `django-backend`:

```powershell
Set-Location .\backend
pipenv lock
```

## 2. Configure Django

In `backend/config/settings.py`:

Add `"corsheaders"` to `INSTALLED_APPS`.

Add `"corsheaders.middleware.CorsMiddleware"` to `MIDDLEWARE` immediately
before `"django.middleware.common.CommonMiddleware"`.

Add this setting alongside the other environment-based settings:

```python
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=Csv(),
)
```

Optionally expose the download filename header if the browser should read it
from a cross-origin export response:

```python
CORS_EXPOSE_HEADERS = ["Content-Disposition"]
```

Do not use `CORS_ALLOW_ALL_ORIGINS = True`; it is not needed for this app.

## 3. Configure the Render service

Set Render environment variable `CORS_ALLOWED_ORIGINS` to the exact deployed
frontend origins, comma-separated if there is more than one, for example:

```text
https://your-ledgerly-project.vercel.app,https://expenses.example.com
```

Do not include URL paths or a trailing slash. Add only origins that are
actually used. Redeploy Render after updating the dependency, middleware,
settings, and environment variable.

## 4. Verify after deploy

From the deployed Vercel site, test an unauthenticated request and an
authenticated request. In the browser network panel, confirm that API
responses include the correct `Access-Control-Allow-Origin` for the Vercel
origin and that preflight `OPTIONS` requests succeed. Re-test CSV export if
the filename header exposure was enabled.

The local Vite development proxy does not need this CORS patch because the
browser only calls its local origin during development.
