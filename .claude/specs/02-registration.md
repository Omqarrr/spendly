# Spec: Registration

## Overview
The registration feature allows users to create accounts in Spendly by providing their name, email, and password. This is the first step in setting up user authentication for the app. On success the user is shown with a success message and then redirected to the login page. This is the entry point for all authenticated features that follow.

## Depends on
- Database setup (Step 1: database-setup)

## Routes
- `POST /register` – User registration endpoint (logged-out access)

## Database changes
- New `users` table structure (defined in Step 1)
- Email uniqueness constraint enforced

## Templates
- **Modify:** `templates/register.html` (form for registration)

## Files to change
- `database/db.py` – Add `register_user()` function
- `app.py` – Add `/register` POST route handler

## Files to create
- None

## New dependencies
- No new pip packages

## Rules for implementation
- Use Werkzeug's `generate_password_hash()` for password hashing
- Validate email format on signup
- Redirect to `/profile` on successful registration
- Handle database errors gracefully

## Definition of done
- [ ] `/register` route implemented
- [ ] User creation logic in `db.py`
- [ ] `register.html` updated with form
- [ ] Success/failure messages displayed
- [ ] Tests pass for registration flow

- GET /register renders the registration form without errors
- Submitting the form with all valid fields creates a new user in users and redirects to /login
- Submitting with mismatched passwords re-renders the form with an error message, no DB insert
- Submitting with an already-registered email re-renders the form with "Email already registered" error
- Submitting with any empty field re-renders the form with a validation error
- Password is stored as a hash — never plaintext — verifiable by inspecting spendly.db
- No duplicate user is created on repeated valid submissions with the same email