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


## Research & documentation log — 2026-09-29

SaMaWi Dating is being developed as both a dating product and a documented privacy/anti-scam case study. Preserve design decisions, observations, test cases, false positives, failures and countermeasures.

### Core communication principle

**Du musst SaMaWi Dating nicht verlassen, um jemanden kennenzulernen.**

SaMaWi will provide its own person-to-person messaging. Users should not have to disclose private email addresses, phone numbers or third-party messenger identities merely to begin a conversation. Legitimate established users may eventually exchange contact information; the goal is to stop coercive or suspicious early migration, not normal relationships.

### Observed off-platform migration patterns

Real-world observations motivating the design (personal identifiers deliberately omitted):

1. A first-contact message used generic relationship language, supplied little/no verifiable profile information, explained this with prior bad experiences, and immediately requested an email exchange.
2. A separate first-contact message immediately supplied three off-platform channels at once: Telegram, Zangi and email, asking the recipient to continue there.
3. A useful behavioral test is to decline migration and ask to continue on-platform. Natural conversation differs from repeating the migration request or abandoning the conversation.

These observations are examples, not proof that an individual sender is fraudulent. SaMaWi should classify behavior and risk signals rather than label people from one message.

### Planned anti-scam signals

- very new account
- generic/repeated first-contact text
- rapid or bulk messaging
- Telegram, Zangi, WhatsApp, Signal or similar identifiers
- email addresses and phone numbers
- external URLs
- obfuscated contact data intended to evade filters
- immediate/repeated requests to leave SaMaWi
- several off-platform channels in one early message
- repeated migration pressure after the recipient declines

Signals should accumulate into a risk score. A single keyword must not automatically establish fraud. Document thresholds, moderation outcomes and false-positive tests.

### Research methodology

For every anti-scam rule/model change retain: hypothesis; anonymized example/pattern; detected features; expected response; actual result; false positives/negatives; revision; date; relevant commit.

Do not commit personal email addresses, telephone numbers, messenger handles, private messages with identifying details, credentials or secrets to this public repository. Research examples must be anonymized/minimized.

### Possible public/CCC case-study direction

Future technical question: **How can a dating platform make common off-platform scam migration harder without blocking normal human conversation?**

A credible case study should show data and engineering rather than marketing: observed patterns, threat model, detection design, privacy constraints, experiments, failure cases, false-positive rates and implementation evolution.

### Current product milestone

- Email verification is live and tested.
- migrations/0004_sessions.sql has been applied.
- Login, password verification, D1 sessions, secure cookie and protected profile route are tested in production.
- Shared fixed header and DE/EN/FR/IT language handling are being expanded.
- Profile setup implementation is in progress.
- Language selector is a stable right-aligned dropdown; DE/EN/FR/IT active, more planned.
