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
- Registration now performs server-side 18+ gating and server-side Turnstile validation before any account data is persisted

### Product decisions
- Platform is 18+ only.
- Phase 1 age gate: birth date plus server-side 18+ calculation.
- Later age verification should use a specialist provider; SaMaWi should retain the verification result rather than copies of identity documents wherever possible.
- Trust & Safety is part of the core design: detect mass messaging, repeated text and suspicious attempts by new accounts to move conversations immediately to Telegram, Zangi, WhatsApp, email, phone numbers or external URLs.
- Legitimate established users must still be able to exchange contact information.
- No pay-per-message model.
- SMW Donate/donations are explicitly deferred until the dating platform itself is stable and operational.

### Current task
Complete secure account creation after the now-implemented Turnstile and 18+ registration gate.

Planned Turnstile widget:
- Name: `samawi-dating-registration`
- Hostname: `dating.samawi.co.uk`
- Widget mode: `Managed`
- Pre-clearance / “Skip future security rule challenges for verified visitors”: OFF

Next:
1. Secure password handling and account creation.
2. Email verification.
3. Login/session handling.
4. Profile creation and local discovery.
5. Later add specialist age verification before opening the platform broadly to real users.
