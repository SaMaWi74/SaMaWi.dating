# SaMaWi Dating

Local-first dating for real people, clear intentions and safer conversations.

Production target: **dating.samawi.co.uk**

## MVP principles

- 18+ only
- Local search with privacy-preserving distance
- Clear dating intentions
- Search plus likes/matches
- Free person-to-person messaging
- Activity status and inactive-profile filtering
- Reporting, blocking and moderation from day one
- Anti-scam protection for new accounts and off-platform contact attempts
- No pay-per-message model
- No donation/payment integration until the core platform is running reliably

## Cloudflare-native stack

- Cloudflare Python Workers
- FastAPI
- Cloudflare D1
- Cloudflare R2 for profile media (next step)
- Cloudflare Turnstile for anti-bot protection (next step)
- Durable Objects/WebSockets when realtime chat is introduced

GitHub is the authoritative project state.


## Cloudflare deployment

Python dependencies such as FastAPI are bundled by **pywrangler**. Use `uv run pywrangler deploy` rather than plain `wrangler deploy`.


Deployment trigger: Cloudflare Git integration configured for Python Workers.


## Current project status — 2026-09-28

### Live infrastructure
- Production domain: `https://dating.samawi.co.uk`
- Health endpoint: `/health` returns `{"status":"healthy","database":"D1"}`
- GitHub repository: `SaMaWi74/SaMaWi.dating` (authoritative source)
- Cloudflare Git deployment from `main`
- Deploy command: `uv run pywrangler deploy`
- D1 database: `samawi-dating`, EU jurisdiction
- D1 binding: `DB`
- Initial D1 migration `migrations/0001_initial.sql` has been applied successfully
- Landing page and registration UI are deployed
- Turnstile widget configured for `dating.samawi.co.uk`; secret stored only as Cloudflare Worker secret `TURNSTILE_SECRET_KEY`
- Registration performs server-side 18+ gating and server-side Turnstile validation
- Account creation code now stores only a salted PBKDF2 password hash and creates new users as `pending`
- Migration `migrations/0002_credentials.sql` adds `password_hash` and `email_verified_at`; it must be applied to production D1 before testing account creation

### Product decisions
- Platform is 18+ only.
- Phase 1 age gate: birth date plus server-side 18+ calculation.
- Later age verification should use a specialist provider; SaMaWi should retain the verification result rather than copies of identity documents wherever possible.
- Trust & Safety is part of the core design: detect mass messaging, repeated text and suspicious attempts by new accounts to move conversations immediately to Telegram, Zangi, WhatsApp, email, phone numbers or external URLs.
- Legitimate established users must still be able to exchange contact information.
- No pay-per-message model.
- SMW Donate/donations are explicitly deferred until the dating platform itself is stable and operational.

### Current task
Apply `migrations/0002_credentials.sql` to production D1, test account creation, then implement email verification.

Planned Turnstile widget:
- Name: `samawi-dating-registration`
- Hostname: `dating.samawi.co.uk`
- Widget mode: `Managed`
- Pre-clearance / “Skip future security rule challenges for verified visitors”: OFF

Next:
1. Apply and test credential migration/account creation.
2. Email verification.
3. Login/session handling.
4. Profile creation and local discovery.
5. Later add specialist age verification before opening the platform broadly to real users.


## Latest milestone

- Real account creation is working in production: Turnstile + server-side 18+ check + PBKDF2-SHA256 password hashing (100,000 iterations, random salt) + D1 insert and read-back verification.
- New accounts are stored with `status = pending` until email verification is implemented.
- Next task: email verification, then login/session handling.


## Production milestone — 2026-09-29

- Registration → Resend verification email → `/verify-email` → account activation has been tested successfully in production.
- SPF and DKIM pass at Gmail; DMARC monitoring record `v=DMARC1; p=none;` is configured for `dating.samawi.co.uk`.
- Login implementation added for active accounts with PBKDF2 password verification and 30-day HttpOnly/Secure/SameSite=Lax session cookie.
- Login UI supports DE/EN/FR/IT and introduces the shared fixed navigation header. Profile setup is protected by the session.
- Migration `migrations/0004_sessions.sql` must be applied to production D1 before login testing.
