# TallyDan — Expense Tracker Frontend

Responsive React + TypeScript frontend for the existing Django REST API.

## Local development

Start the backend and frontend in separate PowerShell terminals. In the
backend terminal:

```powershell
Set-Location 'C:\Dell\Project Github\expense_tracker-backend-cors\backend'
$env:SECRET_KEY = [guid]::NewGuid().ToString('N')
$env:DEBUG = 'True'
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
pipenv run python manage.py runserver 127.0.0.1:8000
```

This uses the backend checkout's local SQLite database at
`backend\db.sqlite3`. The generated secret is temporary and the database URL
is cleared in this terminal so the backend uses its local SQLite default. Do
not run migrations against a database until you have verified its target.

In the frontend terminal:

```powershell
Set-Location 'C:\Dell\Project Github\expense_tracker\frontend'
if (-not (Test-Path .env.local)) { Copy-Item .env.example .env.local }
npm install
npm run dev
```

Open `http://localhost:5173`. In development, the Axios client keeps using
relative `/api/v1/...` paths and Vite forwards `/api` to
`http://127.0.0.1:8000` by default, preserving the request path. To override
the target for a local development session, set `API_PROXY_TARGET` in
`.env.local`; it is read by Vite's server configuration, not used as the
browser API base URL. `.env.local` is ignored by Git.

For production builds, set `VITE_API_BASE_URL` to the API origin only (for
example `https://expense-tracker-api-n5s7.onrender.com`); do not append
`/api/v1`. An empty value in a production build uses the configured Render API
origin. Never put credentials or secrets in frontend environment variables.

Vite serves the app at the local URL printed by `npm run dev`. Use a real API
account; the UI does not contain demo financial data.

## Quality checks

```powershell
npm run lint
npm test
npm run build
```

The production build is written to `dist/`.

## API and authentication

Requests use the verified `/api/v1/` contract documented in
[`../docs/API_CONTRACT.md`](../docs/API_CONTRACT.md). JWTs are held in
`sessionStorage` for the current tab and access tokens are refreshed through
the backend refresh endpoint when supported. Browser storage is accessible to
JavaScript and is not equivalent to an HttpOnly cookie.

The Vite development proxy preserves browser-origin requests while forwarding
`/api` traffic to the local Django backend. Production requests go directly to
the configured API origin.

To confirm local routing, open browser DevTools → Network while using the
frontend. API requests should show a browser request URL beginning with
`http://localhost:5173/api/v1/`; the same request should appear in the local
Django runserver terminal. The browser intentionally talks to Vite, which
proxies the request to `127.0.0.1:8000`.

Expense dates are limited in the client to today or earlier because
`occurred_on` represents when an expense happened. The expense forms and CSV
file selection reject future dates. This is a usability check, not a security
boundary: matching date validation is still required in the Django
serializer/API, including CSV imports and duplicated expenses.

## Vercel deployment

1. Create a Vercel project linked to this repository and set **Root Directory**
   to `frontend/`.
2. Use `npm run build` as the build command and `dist` as the output directory;
   these are also recorded in `vercel.json`.
3. Add the Vercel production domain to the backend's `CORS_ALLOWED_ORIGINS`
   environment variable after applying the separate backend patch in
   [`../docs/BACKEND_CORS_PATCH.md`](../docs/BACKEND_CORS_PATCH.md).
4. Set `VITE_API_BASE_URL` in Vercel to
   `https://expense-tracker-api-n5s7.onrender.com`, redeploy, then test
   registration/login and authenticated data operations on the deployed site.

The backend currently has no CORS middleware or allowed-origin configuration.
Until the patch is applied and the Django service is redeployed, production
browser requests from the Vercel domain will be blocked by the browser's
same-origin policy. Local proxy testing does not require that production CORS
change.

## Current limitations

- The backend accepts any three ASCII letters as a currency code; it does not
  expose a canonical currency list.
- Currency changes are rejected by the backend while expenses or budgets
  exist. No conversion is performed.
- The API does not provide month-specific statistics; the dashboard derives
  the trend from six real monthly summary responses.
- CSV import is limited to 10 MB in this client. The backend source currently
  has no explicit upload-size limit; the UI limit is a client-side safeguard.
