# Expense Tracker frontend instructions

- Frontend work belongs in the root `frontend/` directory. Before editing,
  verify the branch is `frontend`; do not switch branches, commit, or push
  unless explicitly requested.
- Do not alter the CLI or Django backend business logic, models, migrations,
  authentication, schema, or deployment configuration in this branch.
- Treat `docs/API_CONTRACT.md` and backend source as the only sources of truth
  for API routes, payloads, response shapes, filters, and financial behavior.
  Verify backend source before adding an API integration; never invent data.
- Use the central Axios client, TanStack Query, typed feature API functions,
  React Hook Form/Zod, reusable accessible Radix/shadcn-style UI components,
  and currency formatting helpers. Mutations must invalidate affected queries.
- Keep JWTs in the isolated tab-scoped session storage module; do not log
  tokens or passwords, and do not claim browser storage is equivalent to
  HttpOnly cookies.
- Never submit server-owned expense fields (`user`, `currency`, `id`, or
  timestamps). Respect backend user scoping and currency-change restrictions.
- Keep API CORS changes documented in `docs/BACKEND_CORS_PATCH.md`; apply
  them only in a separately authorized `django-backend` change.
- Run relevant `npm run lint`, `npm test`, and `npm run build` checks after
  frontend changes. Do not report checks as successful unless run.
