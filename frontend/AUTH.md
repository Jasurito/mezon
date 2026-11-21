# Accounts and Google SSO

**Status (2026-11-21): implemented.** The backend serves the endpoints below (`backend/app/api/auth.py`), and the
frontend uses them in live mode (`NEXT_PUBLIC_API_MODE=live`; `lib/auth`, `store/user.ts`). Production settings and how
to enable Google are in `deploy/vm1/README.md` ("Accounts"). The rest of this file is the original proposal, kept for
the reasoning.

Frontend behaviour in live mode:
- After sign-in the active learner id becomes the account id: the backend moved the guest's sessions and quiz attempts
  to the account (`guest_user_id`), so the guest id is dropped. Signing out starts a new guest.
- "Continue with Google" is shown only with `NEXT_PUBLIC_GOOGLE_AUTH=true` (the server returns 503 without credentials).
- A failed Google sign-in returns to `/?auth_error=google`; `components/site/auth-error-notice.tsx` explains it.
- 429 (rate limit), 422 (validation) and network errors have their own messages in the form.

## 1. Flow (OAuth 2.0 Authorization Code with PKCE, handled entirely by the backend)

```
Browser                     mezon.modeus.cc (nginx)                 Google
  | "Continue with Google"        |                                     |
  |-- GET /api/auth/google/start?next=/uz/dashboard&guest_user_id=… --->|
  |                               | backend: state + PKCE in a short cookie
  |<-- 302 accounts.google.com/o/oauth2/v2/auth?...&redirect_uri=https://mezon.modeus.cc/api/auth/google/callback
  |------------------------------------------------------ consent ---->|
  |<-- 302 /api/auth/google/callback?code=…&state=… --------------------|
  |                               | backend: check state, exchange code, verify id_token
  |                               | (iss, aud, exp, email_verified), upsert user by Google `sub`
  |<-- 302 next  + Set-Cookie: mezon_session=…; HttpOnly; Secure; SameSite=Lax; Path=/
```

- **Same origin.** nginx serves `/api/*` from FastAPI on `mezon.modeus.cc`. The cookie is first-party, so there's no CORS and no token in `localStorage`.
- **Library.** `authlib` (Starlette integration) on the backend. Scopes: `openid email profile`, nothing more.
- **Identity key.** Use the Google `sub` claim, not the email: emails can change.
- **Session.** An opaque random id in a `sessions` table (revocable), with a 30-day sliding expiry. Avoid long-lived JWTs in cookies.

## 2. Endpoints the frontend expects

| Method | Path | Body | Response |
|---|---|---|---|
| GET | `/api/auth/google/start` | query: `next`, `guest_user_id?` | 302 to Google |
| GET | `/api/auth/google/callback` | from Google | 302 to `next` + cookie |
| POST | `/api/auth/signup` | `{display_name, email, password, guest_user_id}` | `AccountUser`, 409 if the email exists |
| POST | `/api/auth/login` | `{email, password, guest_user_id}` | `AccountUser`, 401 if wrong |
| POST | `/api/auth/logout` | – | 204, clears the cookie |
| GET | `/api/auth/me` | – | `AccountUser` or 401 |

`AccountUser = { id, display_name, email, provider: "google" | "email", avatar_url? }`

Mezon is for everyone: there is no "lawyer / non-lawyer" choice. (A short-lived `users.audience` field from migration 0007 was removed again in 0008.)

Email/password is optional. If you keep it, use argon2id, rate-limit `/login`, and add email verification later. For the hackathon, **Google-only is enough**: the email form can be hidden behind a flag.

## 3. Guest progress (no data loss)

The spec's anonymous `user_id` (a UUID in localStorage) already owns sessions and quiz attempts.
On login or signup the frontend sends `guest_user_id`. The backend should **link** it to the account (`users.account_id = …`), not copy rows. Then the dashboard, results and learning gain all survive sign-in.
The existing API stays the same: `/api/users/{user_id}/dashboard` keeps working, and the backend should check that the cookie's account owns that `user_id`.

## 4. Google Cloud setup (≈10 min)

1. Google Cloud Console → APIs & Services → **OAuth consent screen**: External, app name "Mezon", support email, scopes `openid email profile`. Add the team as test users (no verification is needed while the app is in "Testing").
2. **Credentials → Create OAuth client ID → Web application**
   - Authorized JavaScript origins: `https://mezon.modeus.cc`
   - Authorized redirect URIs: `https://mezon.modeus.cc/api/auth/google/callback` (plus `http://localhost:8000/api/auth/google/callback` for local development)
3. Put `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` and `SESSION_SECRET` in the backend `.env`, never in the frontend or in git.

## 5. Suggestions

- **Personal data law.** Before storing real accounts, ask the team's lawyer to check the Uzbekistan Law "On Personal Data" (ЗРУ-547). It has a localization rule for citizens' personal data and needs a consent text. The jury includes the Ministry of Justice, so this point counts. The sign-up form already has a consent checkbox. Link it to a short privacy notice (what is stored: name, email, game results; why; how to delete).
- **Collect as little as possible.** Store only the `sub`, name, email and avatar URL. Don't keep Google access or refresh tokens: we don't call Google APIs after login.
- **Roles later.** Add `role: student | teacher` to the account now, defaulting to `student`. The spec's teacher/group view (`group_id`) then plugs in without a migration.
- **OneID.** Uzbekistan's government SSO (OneID) is a strong story for the Ministry of Justice track. Mention it on the roadmap slide; don't build it this weekend.
- **Security basics.**
  - Verify the OAuth `state` and the PKCE verifier.
  - Validate `next` as a relative path (`/^\/(uz|uz-cyrl|ru)\//`) to avoid an open redirect.
  - Use `SameSite=Lax` cookies and require CSRF protection (a double-submit token or `Origin` check) on POST endpoints.
  - Rate-limit the auth endpoints (nginx `limit_req` is already used on this VM).
- **Logout everywhere.** Delete the server session row so stolen cookies die.
