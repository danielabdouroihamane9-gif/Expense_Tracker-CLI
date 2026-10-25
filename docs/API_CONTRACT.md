# Verified Expense Tracker API Contract

This contract was verified against the checked-in Django URL configurations,
serializers, viewsets, settings, and API tests. The frontend uses the
`https://expense-tracker-api-n5s7.onrender.com` origin and the exact paths
below. All URLs include a trailing slash.

## Common behavior

- API prefix: `/api/v1/`.
- The frontend authenticates with JWT through the bearer Authorization
  header. The backend also enables DRF `SessionAuthentication`.
- Default permissions are authenticated. Registration, token obtain, and token
  refresh explicitly allow anonymous requests.
- Expenses and budgets are scoped to the authenticated user on the server.
- DRF page-number pagination is configured globally with `PAGE_SIZE = 20`.
  List responses have `{ "count": number, "next": string | null,
  "previous": string | null, "results": [] }`. Lists accept `page`.
- Serializer validation errors use HTTP 400 and generally return field keys
  with arrays of messages; authentication errors use HTTP 401. Missing
  user-scoped detail objects return HTTP 404. Successful deletes return HTTP
  204 with no body.
- Persisted decimal amounts are returned as decimal strings with two
  fractional digits. Dates use `YYYY-MM-DD`; timestamps are ISO 8601.
- Expense categories are exactly: `food`, `transport`, `rent`, `utilities`,
  `entertainment`, `healthcare`, `shopping`, and `other`.

## Authentication and account

### `POST /api/v1/auth/register/`

Anonymous JSON request:

```json
{
  "username": "required, max 150 characters",
  "email": "optional; blank is accepted",
  "password": "required",
  "password_confirm": "required and must equal password",
  "currency": "optional; defaults to USD"
}
```

The password is checked by Django's configured similarity, minimum-length,
common-password, and numeric-password validators. Currency is normalized to
uppercase and must contain exactly three ASCII letters (a format check, not a
validation against an ISO currency catalogue). Username must be unique.

Returns HTTP 201 with:

```json
{
  "id": 1,
  "username": "string",
  "email": "string",
  "currency": "three-letter string or null",
  "date_joined": "ISO 8601 timestamp"
}
```

Registration does not return tokens or automatically sign in the new user.

### `POST /api/v1/auth/token/`

Anonymous JSON request: `username` and `password` (the Django username is the
login identifier; email login is not implemented by this endpoint).

Returns HTTP 200: `{ "refresh": "JWT string", "access": "JWT string" }`.
Invalid credentials return HTTP 401. The access-token lifetime is 15 minutes;
the refresh-token lifetime is 7 days. The configured SimpleJWT settings do
not enable refresh-token rotation or blacklisting.

There is no logout endpoint in the checked-in URL configuration. Frontend
sign-out clears the tab's stored tokens and cached user data; it cannot
revoke a refresh token that was copied before sign-out. Such a token remains
valid until its configured expiry.

### `POST /api/v1/auth/token/refresh/`

Anonymous JSON request: `{ "refresh": "JWT string" }`. Returns an access
token in `{ "access": "JWT string" }`. Refresh failures return an
authentication/validation error.

### `GET /api/v1/auth/me/`

Authenticated; no request body. Returns the registration profile shown above.
`currency` is read from the related settings row and may be `null` if the row
is missing.

### `GET /api/v1/auth/settings/`

Authenticated; returns `{ "currency": "three-letter string" }`.

### `PATCH /api/v1/auth/settings/`

Authenticated JSON request: `{ "currency": "three-letter string" }`.
Currency is normalized to uppercase and must match `[A-Z]{3}`. Returns the
updated settings object. A changed currency is rejected with HTTP 400 if the
user has any expenses or budgets; the error explains that no conversion is
performed. Submitting the existing currency is allowed.

## Expenses

### `GET /api/v1/expenses/`

Authenticated, user-scoped and paginated. Each result has:

```json
{
  "id": "UUID string",
  "user": "integer user id",
  "occurred_on": "YYYY-MM-DD",
  "amount": "decimal string",
  "currency": "three-letter string",
  "category": "one supported category",
  "description": "non-blank string, max 500 characters",
  "created_at": "ISO 8601 timestamp"
}
```

Supported query parameters:

| Parameter | Meaning |
| --- | --- |
| `category` | Exact category match |
| `occurred_on` | Exact date |
| `occurred_on__gte`, `occurred_on__lte` | Inclusive date bounds |
| `amount__gte`, `amount__lte` | Inclusive amount bounds |
| `search` | Searches `description` |
| `ordering` | Comma-separated fields: `occurred_on`, `amount`, `created_at`, `category`; prefix `-` for descending |
| `page` | Page number, 20 results per page |

Default ordering is `-occurred_on,-created_at`.

### `POST /api/v1/expenses/`

Authenticated JSON request:

```json
{
  "occurred_on": "YYYY-MM-DD",
  "amount": "positive decimal with at most 16 integer and 2 fractional digits",
  "category": "one supported category",
  "description": "non-blank string, max 500 characters"
}
```

The backend assigns the authenticated owner and configured currency. Do not
submit `id`, `user`, `currency`, or `created_at`; supplying a protected field
is rejected. Returns the created expense with HTTP 201.

### `GET /api/v1/expenses/{uuid}/`

Authenticated; returns one expense belonging to the user, or HTTP 404.

### `PATCH /api/v1/expenses/{uuid}/`

Authenticated; accepts any editable subset of the create fields and returns
the updated expense. `PUT` is also provided by the ModelViewSet and requires
the complete editable representation.

### `DELETE /api/v1/expenses/{uuid}/`

Authenticated; deletes the user's expense and returns HTTP 204.

### `POST /api/v1/expenses/{uuid}/duplicate/`

Authenticated JSON request: `{ "occurred_on": "YYYY-MM-DD" }`. The server
copies amount, currency, category, and description from the user-owned source
expense and uses the supplied date. Returns the new expense with HTTP 201.

### `GET /api/v1/expenses/summary/`

Authenticated. Optional query parameters `year` and `month` must be supplied
together; `year` is 1–9999 and `month` is 1–12. If omitted, the backend uses
the server's current local month.

Response:

```json
{
  "year": 2026,
  "month": 10,
  "currency": "three-letter string or null",
  "total_spent": "decimal string",
  "categories": [
    {
      "category": "food",
      "label": "Food",
      "spent": "decimal string",
      "budget": "decimal string or null",
      "remaining": "decimal string or null",
      "percentage_used": "decimal string or null"
    }
  ]
}
```

`categories` contains every supported category, including categories without
expenses. `remaining` and `percentage_used` are `null` when no budget exists
for that category. The endpoint includes the user's budget amounts for the
selected month's comparison.

### `GET /api/v1/expenses/statistics/`

Authenticated; uses the same expense filters/search/ordering as the list.
Statistics cover all matching expense history (there is no year/month
parameter), and the response is not paginated:

```json
{
  "count": 0,
  "total_spending": "decimal string",
  "average_expense": "decimal string",
  "highest_expense": "Expense or null",
  "lowest_expense": "Expense or null",
  "spending_by_category": [
    { "category": "food", "total": "decimal string", "count": 0 }
  ],
  "top_categories": ["first five entries from spending_by_category"]
}
```

The statistics object does not contain a currency field; each returned
expense has its own currency. The account settings currency is used to format
aggregate values.

### `GET /api/v1/expenses/export/`

Authenticated CSV attachment; supports the expense list filters/search and
ordering. It exports all matching user-owned records (not just one page).
The CSV has a UTF-8 BOM and columns:
`id, occurred_on, amount, currency, category, description, created_at`.
The response filename is `expenses-YYYY-MM-DD.csv`.

### `POST /api/v1/expenses/import/`

Authenticated multipart form request with a `.csv` upload in field `file`.
Accepted headers (case-insensitive): legacy CLI `Date,Amount,Category,
Description` (currency optional), or Django export fields
`id,occurred_on,amount,currency,category,description,created_at`. `id` and
`created_at` are ignored. Required data fields are date, amount, category,
and description. Dates must be strict `YYYY-MM-DD`; amounts must be positive
and are rounded to two places using `ROUND_HALF_UP`; supplied currency must
match the account currency. Categories and descriptions follow the expense
serializer validation rules. The file must be UTF-8. Unknown, duplicate, or
empty columns and malformed rows are rejected.

Validation is performed for the whole file before writes; if any row is
invalid, the entire import is rejected and no records are created. Exact
duplicates are skipped based on date, amount, category, description, and
currency (including duplicates within the uploaded file).

Success response (HTTP 200):

```json
{
  "detail": "CSV import completed.",
  "rows_processed": 2,
  "imported": 1,
  "skipped_duplicates": 1
}
```

Errors use HTTP 400 with a `detail` string; row errors are additionally
returned as `errors: [{ "row": 2, "errors": { "amount": ["..."] } }]`.
The backend source does not set an explicit maximum upload size. The frontend
applies a 10 MB client-side limit.

## Budgets

### `GET /api/v1/budgets/`

Authenticated, user-scoped and paginated (20 per page). Each result is:

```json
{ "id": 1, "user": 1, "category": "food", "amount": "decimal string" }
```

Supported filters/orderings: `category` exact match; `ordering` by `category`
or `amount` (prefix `-` for descending); `page` for pagination. Default
ordering is `category`.

### `POST /api/v1/budgets/`

Authenticated JSON request: `{ "category": "supported category", "amount":
"positive decimal, at most 16 integer and 2 fractional digits" }`.
The authenticated user is assigned by the backend. `user` is read-only.
Only one budget per category per user is allowed. Duplicate categories and
non-positive amounts return HTTP 400. Returns a budget with HTTP 201.

### `GET /api/v1/budgets/{id}/`, `PATCH /api/v1/budgets/{id}/`,
`PUT /api/v1/budgets/{id}/`, `DELETE /api/v1/budgets/{id}/`

Authenticated and user-scoped. Detail id is an integer. `PATCH` accepts an
editable subset of category/amount; `PUT` requires a full editable
representation. The unique user/category business rule is checked on
updates. Delete returns HTTP 204.

## CORS status

The checked-in backend settings do not install `django-cors-headers`, add its
middleware, or configure allowed origins. Production browser integration from
Vercel therefore requires the separate change described in
[`BACKEND_CORS_PATCH.md`](./BACKEND_CORS_PATCH.md). That patch is not applied
to the `frontend` branch.
