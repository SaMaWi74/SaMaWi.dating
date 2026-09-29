from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from datetime import date
import json
import urllib.parse
import base64
import hashlib
import secrets
import uuid
from js import crypto, TextEncoder, Uint8Array, Array
from workers import fetch
from workers import asgi

app = FastAPI(title="SaMaWi Dating", version="0.2.0")
Default = asgi.entrypoint(app)

HOME = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SaMaWi Dating</title>
<style>
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,sans-serif;background:#101114;color:#f6f6f6}
nav{height:72px;display:flex;align-items:center;justify-content:space-between;max-width:1120px;margin:auto;padding:0 24px}
.brand{font-size:24px;font-weight:800}.brand span{color:#ff5c72}
nav a{color:#fff;text-decoration:none;margin-left:22px}.cta{background:#ff5c72;padding:11px 18px;border-radius:999px;font-weight:700}
main{max-width:1120px;margin:auto;padding:90px 24px 70px;display:grid;grid-template-columns:1.15fr .85fr;gap:70px;align-items:center}
h1{font-size:clamp(46px,7vw,78px);line-height:.98;margin:0 0 25px}h1 em{font-style:normal;color:#ff5c72}
.lead{font-size:20px;line-height:1.6;color:#c9cbd1;max-width:650px}.actions{margin-top:34px;display:flex;gap:14px;flex-wrap:wrap}
.button{display:inline-block;padding:15px 24px;border-radius:999px;text-decoration:none;font-weight:800}.primary{background:#ff5c72;color:white}.secondary{border:1px solid #4a4d55;color:white}
.card{background:#1b1d22;border:1px solid #30333b;border-radius:28px;padding:32px;box-shadow:0 30px 80px #0008}
.card h2{margin-top:0;font-size:28px}.row{padding:15px 0;border-bottom:1px solid #30333b}.row:last-child{border:0}.check{color:#67dda0;font-weight:800;margin-right:10px}
footer{text-align:center;color:#777;padding:40px 20px}
@media(max-width:800px){main{grid-template-columns:1fr;padding-top:45px}.card{margin-top:10px}}
</style>
</head>
<body>
<nav><div class="brand">SaMaWi<span>.</span>dating</div><div><a href="/login">Anmelden</a><a class="cta" href="/register">Kostenlos registrieren</a></div></nav>
<main>
<section><h1>Echte Menschen.<br><em>Echte Nähe.</em></h1>
<p class="lead">Dating ohne Karteileichen, versteckte Kosten und künstliche Chats. Finde Menschen in deiner Nähe, die klar sagen, was sie suchen.</p>
<div class="actions"><a class="button primary" href="/register">Jetzt kostenlos starten</a><a class="button secondary" href="#why">Warum SaMaWi?</a></div></section>
<section class="card" id="why"><h2>Dating, wie es sein sollte.</h2>
<div class="row"><span class="check">✓</span>Lokale Suche statt Bezirk-Chaos</div>
<div class="row"><span class="check">✓</span>Klare Absichten und echte Aktivität</div>
<div class="row"><span class="check">✓</span>Nachrichten ohne Credits pro Nachricht</div>
<div class="row"><span class="check">✓</span>Anti-Scam-Schutz von Anfang an</div>
<div class="row"><span class="check">✓</span>18+ und Privatsphäre by design</div></section>
</main><footer>© 2026 SaMaWi Dating · dating.samawi.co.uk</footer>
</body></html>"""

REGISTER = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Registrieren · SaMaWi Dating</title><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script>
<style>body{font-family:system-ui;background:#101114;color:#fff;margin:0}.box{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}h1{margin-top:0}label{display:block;margin:18px 0 7px;color:#c9cbd1}input{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font-size:16px;box-sizing:border-box}button{width:100%;margin-top:25px;padding:15px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}.note{color:#92959d;font-size:14px;line-height:1.5}a{color:#ff8293}</style></head>
<body><div class="box"><a href="/">← SaMaWi Dating</a><h1>Konto erstellen</h1><p>Der erste Schritt zu deinem Profil.</p>
<form method="post" action="/api/register"><label>E-Mail-Adresse</label><input name="email" type="email" required autocomplete="email"><label>Geburtsdatum</label><input name="birth_date" type="date" required><label>Passwort</label><input name="password" type="password" minlength="10" required autocomplete="new-password"><div style="margin-top:22px" class="cf-turnstile" data-sitekey="0x4AAAAAAFHp5Nw6yg0wNLfG" data-action="register" data-theme="dark"></div><button type="submit">Weiter</button></form>
<p class="note">SaMaWi Dating ist ausschließlich für Erwachsene ab 18 Jahren. Dein Geburtsdatum wird serverseitig geprüft. Unter 18 ist keine Registrierung möglich.</p></div></body></html>"""

@app.get("/", response_class=HTMLResponse)
async def root():
    return HOME

@app.get("/register", response_class=HTMLResponse)
async def register():
    return REGISTER

@app.get("/health")
async def health(request: Request):
    env = request.scope["env"]
    result = await env.DB.prepare("SELECT 1 AS ok").first()
    return {"status": "healthy" if result and result.ok == 1 else "degraded", "database": "D1"}


async def hash_password(password: str) -> str:
    # Cloudflare Python Workers run on Pyodide, where hashlib.pbkdf2_hmac is unavailable.
    # Use the Workers Web Crypto implementation of PBKDF2 instead.
    iterations = 600_000
    salt_js = Uint8Array.new(16)
    crypto.getRandomValues(salt_js)
    encoder = TextEncoder.new()
    key_material = await crypto.subtle.importKey(
        "raw",
        encoder.encode(password),
        "PBKDF2",
        False,
        Array.from_(["deriveBits"]),
    )
    derived_js = await crypto.subtle.deriveBits(
        {"name": "PBKDF2", "salt": salt_js, "iterations": iterations, "hash": "SHA-256"},
        key_material,
        256,
    )
    salt = bytes(salt_js.to_py())
    derived = bytes(Uint8Array.new(derived_js).to_py())
    return "pbkdf2_sha256$%d$%s$%s" % (
        iterations,
        base64.urlsafe_b64encode(salt).decode("ascii"),
        base64.urlsafe_b64encode(derived).decode("ascii"),
    )


def registration_result(title: str, message: str, ok: bool = False, status_code: int = 200) -> HTMLResponse:
    accent = "#67dda0" if ok else "#ff8293"
    html = f"""<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · SaMaWi Dating</title><style>body{{font-family:system-ui;background:#101114;color:#fff;margin:0}}.box{{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}}h1{{color:{accent}}}p{{line-height:1.6;color:#c9cbd1}}a{{display:inline-block;margin-top:18px;color:#ff8293}}</style></head>
<body><div class="box"><h1>{title}</h1><p>{message}</p><a href="/register">← Zur Registrierung</a></div></body></html>"""
    return HTMLResponse(html, status_code=status_code)


def is_at_least_18(birth_date: date, today: date | None = None) -> bool:
    today = today or date.today()
    eighteenth_birthday = birth_date.replace(year=birth_date.year + 18)
    return eighteenth_birthday <= today


@app.post("/api/register")
async def create_registration(request: Request):
    raw_body = (await request.body()).decode("utf-8")
    parsed = urllib.parse.parse_qs(raw_body, keep_blank_values=True)
    def field(name: str) -> str:
        values = parsed.get(name, [""])
        return str(values[0]) if values else ""

    email = field("email").strip().lower()
    birth_date_raw = field("birth_date")
    password = field("password")
    token = field("cf-turnstile-response")

    if not email or not birth_date_raw or len(password) < 10 or not token:
        return registration_result("Noch nicht ganz", "Bitte alle Felder korrekt ausfüllen.", status_code=400)

    try:
        birth_date = date.fromisoformat(birth_date_raw)
    except ValueError:
        return registration_result("Ungültiges Geburtsdatum", "Bitte prüfe dein Geburtsdatum.", status_code=400)

    if birth_date > date.today() or not is_at_least_18(birth_date):
        return registration_result("Registrierung nicht möglich", "SaMaWi Dating ist ausschließlich für Personen ab 18 Jahren.", status_code=403)

    env = request.scope["env"]
    secret = str(env.TURNSTILE_SECRET_KEY)
    body = urllib.parse.urlencode({"secret": secret, "response": token})

    verification_response = await fetch(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
    )
    verification = dict(await verification_response.json())

    if (
        not verification.get("success")
        or verification.get("hostname") != "dating.samawi.co.uk"
        or verification.get("action") != "register"
    ):
        return registration_result("Sicherheitsprüfung fehlgeschlagen", "Bitte gehe zurück und versuche es erneut.", status_code=400)

    print("REGISTER stage=turnstile_ok")
    password_hash = await hash_password(password)
    user_id = str(uuid.uuid4())
    print("REGISTER stage=hash_ok")

    try:
        insert_result = await env.DB.prepare(
            "INSERT INTO users (id, email, birth_date, status, password_hash) VALUES (?, ?, ?, 'pending', ?)"
        ).bind(user_id, email, birth_date.isoformat(), password_hash).run()
        print("REGISTER stage=insert_run")
        saved = await env.DB.prepare(
            "SELECT id, status FROM users WHERE id = ?"
        ).bind(user_id).first()
        print("REGISTER stage=insert_verified found=" + ("yes" if saved else "no"))
        if not saved:
            return registration_result(
                "Speichern fehlgeschlagen",
                "Das Konto konnte nicht bestätigt in der Datenbank gespeichert werden.",
                status_code=500,
            )
    except Exception as exc:
        # D1 enforces the unique email constraint. Do not expose database details.
        print("REGISTER stage=insert_error type=" + type(exc).__name__)
        if "UNIQUE" in str(exc).upper():
            return registration_result(
                "E-Mail bereits registriert",
                "Für diese E-Mail-Adresse gibt es bereits ein Konto.",
                status_code=409,
            )
        raise

    print("REGISTER stage=complete")
    return registration_result(
        "Konto angelegt ✓",
        "Dein Konto wurde sicher angelegt. Als Nächstes aktivieren wir die E-Mail-Bestätigung.",
        ok=True,
    )
