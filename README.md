# Employee Task Management System — Backend

Django + Django REST Framework + MySQL backend with JWT authentication, built for the Flutter Full Stack Developer Assessment.

## Live Deployment

| | |
|---|---|
| **Live API base URL** | `https://<your-app-name>.onrender.com` *(fill in after deploying — see below)* |
| **Swagger/API root** | `https://<your-app-name>.onrender.com/` (health check) |
| **Django Admin** | `https://<your-app-name>.onrender.com/admin/` |
| **Test user (mobile app login)** | email: `test@example.com` / password: `TaskManager@2026` |
| **Test admin (Django Admin login)** | email: `admin@example.com` / password: `AdminPass@2026` |

> ⚠️ Render's free tier spins down after inactivity — the first request after idling can take 30–50 seconds. This is expected, not a bug.

---

## Tech Stack & Architecture

- **Framework:** Django 5 + Django REST Framework
- **Auth:** JWT via `djangorestframework-simplejwt` (email-based login, 7-day access tokens)
- **Database:** MySQL (via PyMySQL driver — chosen over `mysqlclient` because it's pure-Python and avoids native build-tool issues during deployment); falls back to SQLite automatically if no `DATABASE_URL` is set, for zero-friction local setup
- **Architecture:** App-per-domain (Django convention) — `accounts` (auth/users) and `tasks` (task CRUD) are fully isolated apps, each owning its own models, serializers, views, urls, and admin config
- **Bonus admin dashboard:** Django Admin is wired up out of the box (view/edit/delete users and tasks, inline status updates) in addition to any separate React admin panel

### Why this structure
- **Separation of concerns:** HTTP layer (views) never touches the ORM directly without going through serializers, so validation is centralized and consistent.
- **Object-level permissions:** a custom `IsOwner` permission plus queryset-level filtering means a user can never view, edit, or delete another user's tasks — even if they guess a task ID.
- **Consistent error contract:** a custom DRF exception handler wraps every error (validation, auth, 404, 500) into `{ "success": false, "message": "...", "errors": {...} }`, so the Flutter client can parse errors the same way regardless of endpoint.

---

## Local Setup

1. Clone the repo and create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Copy the environment file:
   ```bash
   cp .env.example .env
   ```
   By default (`DATABASE_URL` unset) it runs on **SQLite** — good enough to get moving immediately. To use **MySQL** instead, create a database and set:
   ```
   DATABASE_URL=mysql://root:yourpassword@localhost:3306/task_manager
   ```

3. Run migrations and create an admin user:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. Start the server:
   ```bash
   python manage.py runserver
   ```
   API is now live at `http://localhost:8000/`, admin panel at `http://localhost:8000/admin/`.

---

## Deploying to Render

1. Push this repo to GitHub.
2. On [render.com](https://render.com) → **New → Web Service** → connect the repo.
3. Settings:
   - **Build command:** `./build.sh` (runs migrations + collects static files automatically)
   - **Start command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
4. Environment variables to add in the Render dashboard:
   - `SECRET_KEY` — any long random string
   - `DEBUG` — `False`
   - `DATABASE_URL` — your MySQL connection string (e.g. from [Aiven](https://aiven.io) or [Railway](https://railway.app) free tier — Render itself doesn't offer free managed MySQL)
   - `ALLOWED_HOSTS` — `.onrender.com` (already defaulted, only needed if using a custom domain)
5. Deploy, then visit `https://<your-app>.onrender.com/` to confirm the health check responds.
6. Create your test user and admin via Render's shell tab, or just call `/api/auth/register/` once it's live.

---

## API Reference

All endpoints are prefixed `/api/`. Authenticated requests need header:
`Authorization: Bearer <access_token>`

### Auth (`/api/auth/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| POST | `register/` | No | `{name, email, password, confirm_password}` → returns tokens + user |
| POST | `login/` | No | `{email, password}` → returns tokens + user |
| POST | `token/refresh/` | No | `{refresh}` → returns new access token |
| GET | `me/` | Yes | Current logged-in user's profile |
| POST | `logout/` | Yes | Acknowledges logout (client discards token) |

### Tasks (`/api/tasks/`)

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| GET | `/?search=&status=&priority=&ordering=` | Yes | List the current user's tasks (paginated, searchable, filterable) |
| POST | `/` | Yes | Create a task |
| GET | `/{id}/` | Yes | Task detail (403/404 if not the owner) |
| PUT/PATCH | `/{id}/` | Yes | Update a task |
| DELETE | `/{id}/` | Yes | Delete a task |

**Task fields:** `title` (required), `description`, `priority` (`Low`/`Medium`/`High`), `status` (`Pending`/`In Progress`/`Completed`), `due_date` (ISO datetime, optional).

---

## Edge Cases Handled

- Duplicate email on registration → `400`
- Password/confirm-password mismatch → `400`
- Weak/common passwords rejected via Django's built-in password validators
- Wrong login credentials → `401`
- Missing/expired/malformed JWT → `401`
- Empty or whitespace-only task title → `400`
- Due date set in the past on creation → `400`
- User A attempting to view/edit/delete User B's task → `404` (task scoped out of their queryset entirely, not just permission-denied — avoids leaking that the task exists)
- All list responses paginated (20/page) to stay stable as task counts grow
- Uncaught server errors never leak stack traces — always a clean `500` JSON response
