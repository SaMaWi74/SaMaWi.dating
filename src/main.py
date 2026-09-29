from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import date, datetime, timedelta, timezone
import urllib.parse
import base64
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



LANGS = {
    "de": {"login":"Anmelden","register":"Kostenlos registrieren","email":"E-Mail-Adresse","password":"Passwort","submit":"Anmelden","title":"Willkommen zurück","bad":"E-Mail oder Passwort ist nicht korrekt.","inactive":"Bitte bestätige zuerst deine E-Mail-Adresse."},
    "en": {"login":"Sign in","register":"Register free","email":"Email address","password":"Password","submit":"Sign in","title":"Welcome back","bad":"Email or password is incorrect.","inactive":"Please confirm your email address first."},
    "fr": {"login":"Connexion","register":"Inscription gratuite","email":"Adresse e-mail","password":"Mot de passe","submit":"Se connecter","title":"Bon retour","bad":"L’e-mail ou le mot de passe est incorrect.","inactive":"Veuillez d’abord confirmer votre adresse e-mail."},
    "it": {"login":"Accedi","register":"Registrati gratis","email":"Indirizzo e-mail","password":"Password","submit":"Accedi","title":"Bentornato","bad":"E-mail o password non corretti.","inactive":"Conferma prima il tuo indirizzo e-mail."},
}

def lang_for(request: Request) -> str:
    q = request.query_params.get("lang", "").lower()
    if q in LANGS:
        return q
    cookie = request.cookies.get("lang", "").lower()
    if cookie in LANGS:
        return cookie
    accept = request.headers.get("accept-language", "").lower()
    for code in ("de","fr","it","en"):
        if code in accept:
            return code
    return "en"

def header_html(lang: str, logged_in: bool = False) -> str:
    t = LANGS[lang]
    auth = '<a href="/logout">Logout</a>' if logged_in else f'<a href="/login?lang={lang}">{t["login"]}</a><a class="cta" href="/register?lang={lang}">{t["register"]}</a>'
    langs = " ".join(f'<a class="lang" href="?lang={x}">{x.upper()}</a>' for x in ("de","en","fr","it"))
    return f'<nav class="top"><a class="brand" href="/?lang={lang}">SaMaWi<span>.</span>dating</a><div class="navright">{langs}{auth}</div></nav>'

async def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iterations_raw, salt_b64, expected_b64 = encoded.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        iterations = int(iterations_raw)
        salt = base64.urlsafe_b64decode(salt_b64.encode("ascii"))
        expected = base64.urlsafe_b64decode(expected_b64.encode("ascii"))
        encoder = TextEncoder.new()
        key_material = await crypto.subtle.importKey("raw", encoder.encode(password), "PBKDF2", False, Array.from_(["deriveBits"]))
        salt_js = Uint8Array.new(len(salt))
        for i, b in enumerate(salt):
            salt_js[i] = b
        derived_js = await crypto.subtle.deriveBits({"name":"PBKDF2","salt":salt_js,"iterations":iterations,"hash":"SHA-256"}, key_material, len(expected) * 8)
        actual = bytes(Uint8Array.new(derived_js).to_py())
        return secrets.compare_digest(actual, expected)
    except Exception:
        return False

def login_page(lang: str, error: str = "") -> str:
    t=LANGS[lang]
    err=f'<p class="err">{error}</p>' if error else ""
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t["login"]} · SaMaWi Dating</title>
<style>*{{box-sizing:border-box}}body{{margin:0;padding-top:72px;font-family:system-ui;background:#101114;color:#fff}}.top{{position:fixed;z-index:10;top:0;left:0;right:0;height:72px;background:#101114eF;backdrop-filter:blur(10px);display:flex;align-items:center;justify-content:space-between;padding:0 max(24px,calc((100vw - 1120px)/2))}}.brand{{font-size:24px;font-weight:800;color:#fff;text-decoration:none}}.brand span{{color:#ff5c72}}.navright{{display:flex;gap:14px;align-items:center}}.top a{{color:#fff;text-decoration:none}}.top .cta{{background:#ff5c72;padding:10px 16px;border-radius:999px;font-weight:700}}.lang{{font-size:12px;color:#aaa!important}}.box{{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}}label{{display:block;margin:18px 0 7px;color:#c9cbd1}}input{{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font-size:16px}}button{{width:100%;margin-top:25px;padding:15px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}}.err{{color:#ff8293}}@media(max-width:700px){{.lang{{display:none}}}}</style></head><body>{header_html(lang)}<main class="box"><h1>{t["title"]}</h1>{err}<form method="post" action="/api/login?lang={lang}"><label>{t["email"]}</label><input name="email" type="email" required autocomplete="email"><label>{t["password"]}</label><input name="password" type="password" required autocomplete="current-password"><button>{t["submit"]}</button></form></main></body></html>'''

@app.get("/login", response_class=HTMLResponse)
async def login(request: Request):
    lang=lang_for(request)
    response=HTMLResponse(login_page(lang))
    response.set_cookie("lang",lang,max_age=31536000,samesite="lax",secure=True)
    return response

@app.post("/api/login")
async def do_login(request: Request):
    lang=lang_for(request); t=LANGS[lang]
    parsed=urllib.parse.parse_qs((await request.body()).decode("utf-8"),keep_blank_values=True)
    email=str(parsed.get("email",[""])[0]).strip().lower()
    password=str(parsed.get("password",[""])[0])
    env=request.scope["env"]
    user=await env.DB.prepare("SELECT id,status,password_hash FROM users WHERE email = ? LIMIT 1").bind(email).first()
    if not user or not await verify_password(password,str(user.password_hash or "")):
        return HTMLResponse(login_page(lang,t["bad"]),status_code=401)
    if str(user.status)!="active":
        return HTMLResponse(login_page(lang,t["inactive"]),status_code=403)
    token=secrets.token_urlsafe(32)
    expires=(datetime.now(timezone.utc)+timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    await env.DB.prepare("INSERT INTO sessions (token,user_id,expires_at) VALUES (?, ?, ?)").bind(token,str(user.id),expires).run()
    response=RedirectResponse("/profile/setup?lang="+lang,status_code=303)
    response.set_cookie("samawi_session",token,max_age=2592000,httponly=True,secure=True,samesite="lax",path="/")
    response.set_cookie("lang",lang,max_age=31536000,secure=True,samesite="lax",path="/")
    return response

@app.get("/logout")
async def logout(request: Request):
    token=request.cookies.get("samawi_session","")
    if token:
        await request.scope["env"].DB.prepare("DELETE FROM sessions WHERE token = ?").bind(token).run()
    response=RedirectResponse("/",status_code=303)
    response.delete_cookie("samawi_session",path="/")
    return response

@app.get("/profile/setup", response_class=HTMLResponse)
async def profile_setup(request: Request):
    lang=lang_for(request)
    token=request.cookies.get("samawi_session","")
    row=None
    if token:
        row=await request.scope["env"].DB.prepare("SELECT user_id FROM sessions WHERE token=? AND expires_at > datetime('now') LIMIT 1").bind(token).first()
    if not row:
        return RedirectResponse("/login?lang="+lang,status_code=303)
    return HTMLResponse(f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Profil · SaMaWi Dating</title><style>body{{margin:0;padding-top:72px;font-family:system-ui;background:#101114;color:#fff}}.top{{position:fixed;top:0;left:0;right:0;height:72px;background:#101114;display:flex;align-items:center;justify-content:space-between;padding:0 max(24px,calc((100vw - 1120px)/2))}}.brand{{font-size:24px;font-weight:800;color:#fff;text-decoration:none}}.brand span{{color:#ff5c72}}.navright{{display:flex;gap:14px;align-items:center}}.top a{{color:#fff;text-decoration:none}}.lang{{font-size:12px;color:#aaa!important}}main{{max-width:760px;margin:70px auto;padding:34px}} </style></head><body>{header_html(lang,True)}<main><h1>Profil einrichten</h1><p>Login funktioniert. Als Nächstes bauen wir hier dein Dating-Profil.</p></main></body></html>''')

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
    iterations = 100_000
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
    years = today.year - birth_date.year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        years -= 1
    return years >= 18


async def send_verification_email(env, email: str, token: str) -> None:
    verify_url = "https://dating.samawi.co.uk/verify-email?token=" + urllib.parse.quote(token)
    payload = {
        "from": "SaMaWi Dating <noreply@dating.samawi.co.uk>",
        "to": [email],
        "subject": "Bestätige deine E-Mail-Adresse · SaMaWi Dating",
        "html": (
            "<h2>Willkommen bei SaMaWi Dating</h2>"
            "<p>Bitte bestätige deine E-Mail-Adresse, um dein Konto zu aktivieren.</p>"
            f'<p><a href="{verify_url}">E-Mail-Adresse bestätigen</a></p>'
            "<p>Der Link ist 24 Stunden gültig. Wenn du dich nicht registriert hast, kannst du diese Mail ignorieren.</p>"
        ),
    }
    response = await fetch(
        "https://api.resend.com/emails",
        method="POST",
        headers={
            "Authorization": "Bearer " + str(env.RESEND_API_KEY),
            "Content-Type": "application/json",
        },
        body=__import__("json").dumps(payload),
    )
    if not response.ok:
        detail = await response.text()
        raise RuntimeError("Resend email failed: HTTP %s %s" % (response.status, detail[:200]))


@app.get("/verify-email", response_class=HTMLResponse)
async def verify_email(request: Request):
    token = request.query_params.get("token", "")
    if not token:
        return registration_result("Ungültiger Link", "Der Bestätigungslink ist unvollständig.", status_code=400)

    env = request.scope["env"]
    row = await env.DB.prepare(
        """SELECT evt.user_id
           FROM email_verification_tokens evt
           JOIN users u ON u.id = evt.user_id
           WHERE evt.token = ? AND evt.used_at IS NULL AND evt.expires_at > datetime('now')
             AND u.email_verified_at IS NULL
           LIMIT 1"""
    ).bind(token).first()

    if not row:
        return registration_result(
            "Link ungültig oder abgelaufen",
            "Dieser Bestätigungslink wurde bereits verwendet oder ist nicht mehr gültig.",
            status_code=400,
        )

    user_id = str(row.user_id)
    await env.DB.prepare(
        "UPDATE users SET email_verified_at = datetime('now'), status = 'active' WHERE id = ?"
    ).bind(user_id).run()
    await env.DB.prepare(
        "UPDATE email_verification_tokens SET used_at = datetime('now') WHERE token = ?"
    ).bind(token).run()
    print("VERIFY_EMAIL stage=complete user_id=" + user_id)
    return registration_result(
        "E-Mail bestätigt ✓",
        "Dein Konto ist jetzt aktiviert. Als Nächstes richten wir dein Profil ein.",
        ok=True,
    )


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

        verification_token = secrets.token_urlsafe(32)
        expires_at = (datetime.now(timezone.utc) + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        await env.DB.prepare(
            "INSERT INTO email_verification_tokens (token, user_id, expires_at) VALUES (?, ?, ?)"
        ).bind(verification_token, user_id, expires_at).run()
        print("REGISTER stage=verification_token_saved")
        await send_verification_email(env, email, verification_token)
        print("REGISTER stage=verification_email_sent")
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
        "Fast geschafft ✓",
        "Dein Konto wurde angelegt. Wir haben dir eine Bestätigungsmail geschickt. Bitte öffne den Link in der Mail innerhalb von 24 Stunden.",
        ok=True,
    )
