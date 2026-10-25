# Ledgerly — Expense Tracker Frontend

Responsive React + TypeScript frontend for the existing Django REST API.

## Local development

From the repository root, in PowerShell:

```powershell
Set-Location .\frontend
Copy-Item .env.example .env.local
npm install
npm run dev
```

Keep `VITE_API_BASE_URL` empty in `.env.local` to use the Vite `/api` proxy to
the deployed Render service. To use another API origin, set this variable to
the origin only (for example `https://api.example.com`); do not append
`/api/v1`. Production builds default to the configured Render API origin when
the variable is empty; set the variable explicitly in Vercel to make the
deployment target clear and override it when using a different API.

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
`/api` traffic to `https://expense-tracker-api-n5s7.onrender.com`. Production
requests go directly to the configured API origin.

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
