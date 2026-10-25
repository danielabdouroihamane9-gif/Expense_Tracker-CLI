# Backend CORS implementation and deployment checklist

The CORS implementation is complete in the local `django-backend` working
tree. The backend changes, dependency lockfile, and focused tests are present;
the full backend test suite has been reported passing (81 tests). These
changes have not been committed, pushed, or deployed. Production CORS will
remain unavailable until the Render environment variable is configured and
the updated backend is deployed.

## Local implementation

- [x] Add `django-cors-headers` to `backend/Pipfile` and
  `backend/Pipfile.lock`.
- [x] Register `corsheaders` in `INSTALLED_APPS`.
- [x] Place `CorsMiddleware` immediately before Django's `CommonMiddleware`.
- [x] Read allowed origins from `CORS_ALLOWED_ORIGINS` using the project's
  environment-based settings convention. An unset value allows no origins.
- [x] Expose `Content-Disposition` so browser code can read CSV download
  filenames.
- [x] Add focused tests for middleware order, allowed and disallowed origins,
  preflight requests carrying `Authorization`, and the exposed CSV header.

Do not enable unrestricted CORS with `CORS_ALLOW_ALL_ORIGINS`.

## Before deployment

- [ ] Confirm the exact origin of the deployed frontend. Use only the scheme
  and hostname, for example `https://<actual-frontend-host>`; do not include
  a URL path or trailing slash. Do not use this illustrative value literally.
- [ ] In the Render service's environment settings, set
  `CORS_ALLOWED_ORIGINS` to that actual deployed frontend origin.
- [ ] If more than one frontend origin is in use, list the origins separated
  by commas, with no paths or trailing slashes.
- [ ] Deploy the backend changes to Render after setting the environment
  variable.

The production frontend URL has not been specified here; do not substitute a
guessed Vercel domain.

## Verify after deployment

Using the deployed frontend origin and browser developer tools:

- [ ] Send a browser preflight `OPTIONS` request to an API endpoint with
  `Authorization` in `Access-Control-Request-Headers`. Confirm it succeeds
  and returns `Access-Control-Allow-Origin` matching the frontend origin,
  with `Authorization` among the allowed headers.
- [ ] Make an authenticated API request from the frontend. Confirm the
  response is readable by the browser and has the matching
  `Access-Control-Allow-Origin`.
- [ ] Export a CSV from the frontend. Confirm the download succeeds and the
  response exposes `Content-Disposition`, allowing the frontend to read the
  filename.
- [ ] Confirm an origin that is not configured does not receive an
  `Access-Control-Allow-Origin` response header.

The local Vite development proxy does not require this production CORS
configuration because the browser calls the local development origin.
