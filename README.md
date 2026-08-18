# BrandActivation — Backend

Flask API server with PostgreSQL (psycopg2) and OTP-based authentication.

---

## Prerequisites

Make sure these are installed on your machine before starting:

| Tool | Version | Download |
|---|---|---|
| Python | 3.10+ | https://python.org/downloads |
| PostgreSQL | 14+ | https://postgresql.org/download |
| pip | latest | comes with Python |

---

## 1. Clone and enter the folder

```bash
cd ba-backend
```

---

## 2. Create a virtual environment

```bash
# Create
python -m venv venv

# Activate — Windows
venv\Scripts\activate

# Activate — macOS / Linux
source venv/bin/activate
```

You should see `(venv)` at the start of your terminal prompt.

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Set up environment variables

Copy the example file and fill in your values:

```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

Open `.env` and update:

```env
# Required — change these
SECRET_KEY=your-random-secret-key
JWT_SECRET_KEY=your-random-jwt-key
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/brandactivation_dev

# Email (for OTP delivery)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

> **Gmail app password:** Go to Google Account → Security → 2-Step Verification → App Passwords. Generate one for "Mail".

---

## 5. Create the database

Open psql or pgAdmin and run:

```sql
CREATE DATABASE brandactivation_dev;
```

---

## 6. Apply the database schema

This creates all tables, indexes, and triggers:

```bash
python scripts/init_db.py
```

You should see:
```
Connecting to PostgreSQL...
Running schema migrations...

  ✓ Applied: Services/user/schema.sql
  ✓ Applied: Services/auth/schema.sql
  ✓ Applied: Services/payment/schema.sql
  ✓ Applied: Services/campaigns/schema.sql

All schemas applied successfully.
```

---

## 7. Start the server

```bash
python app.py
```

The API will be running at: **http://localhost:5000**

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Step 1 — submit name, email, role → OTP sent |
| POST | `/api/auth/verify-register` | Step 2 — verify OTP → account created + JWT |
| POST | `/api/auth/login` | Step 1 — submit email → OTP sent |
| POST | `/api/auth/verify-login` | Step 2 — verify OTP → JWT |
| POST | `/api/auth/logout` | Revoke current JWT |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/users/` | List all users (admin only) |
| GET | `/api/campaigns/` | List campaigns |
| GET | `/api/payments/` | List payments |

---

## Project Structure

```
ba-backend/
├── app.py                  ← App entry point
├── Config/
│   └── settings.py         ← Environment config
├── Core/
│   ├── database.py         ← psycopg2 connection pool
│   ├── extensions.py       ← JWT, Mail
│   ├── middleware.py       ← Auth decorators
│   ├── response.py         ← Standard JSON response helpers
│   └── error_handlers.py   ← Global error handlers
├── Services/
│   ├── auth/               ← Register, login, OTP, logout
│   ├── user/               ← User management
│   ├── payment/            ← Payments
│   └── campaigns/          ← Campaign management
├── Utils/
│   ├── logger.py           ← App-wide logger
│   ├── otp.py              ← OTP generate, hash, send
│   └── helpers.py          ← Shared utilities
└── scripts/
    └── init_db.py          ← Run all schema.sql files
```

---

## Common Commands

```bash
# Run with debug mode
FLASK_DEBUG=1 python app.py

# Re-apply schema after a schema.sql change
python scripts/init_db.py

# Run tests
pytest

# Deactivate virtual environment
deactivate
```

---

## Troubleshooting

**`psycopg2` install fails on Windows**
→ Make sure you are using `psycopg2-binary`, not `psycopg2`. It's already set in `requirements.txt`.

**`connection refused` on port 5432**
→ PostgreSQL is not running. Start it via Services (Windows) or `brew services start postgresql` (Mac).

**OTP email not sending**
→ Check `MAIL_USERNAME` and `MAIL_PASSWORD` in `.env`. Gmail requires an App Password, not your regular account password.
