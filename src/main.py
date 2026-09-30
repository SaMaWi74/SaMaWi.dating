from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

LANGS = {
    "de": {"login":"Anmelden","register":"Kostenlos registrieren","email":"E-Mail-Adresse","password":"Passwort","submit":"Anmelden","title":"Willkommen zurück","bad":"E-Mail oder Passwort ist nicht korrekt.","inactive":"Bitte bestätige zuerst deine E-Mail-Adresse.","birth":"Geburtsdatum","create":"Konto erstellen","next":"Weiter","home_title":"Echte Menschen.","home_near":"Echte Nähe.","home_lead":"Dating ohne Karteileichen, versteckte Kosten und künstliche Chats. Finde Menschen in deiner Nähe, die klar sagen, was sie suchen.","start":"Jetzt kostenlos starten","why":"Warum SaMaWi?","card":"Dating, wie es sein sollte.","rows":["Lokale Suche statt Bezirk-Chaos","Klare Absichten und echte Aktivität","Nachrichten ohne Credits pro Nachricht","Anti-Scam-Schutz von Anfang an","18+ und Privatsphäre by design"],"reg_intro":"Der erste Schritt zu deinem Profil.","adult":"SaMaWi Dating ist ausschließlich für Erwachsene ab 18 Jahren. Dein Geburtsdatum wird serverseitig geprüft."},
    "en": {"login":"Sign in","register":"Register free","email":"Email address","password":"Password","submit":"Sign in","title":"Welcome back","bad":"Email or password is incorrect.","inactive":"Please confirm your email address first.","birth":"Date of birth","create":"Create account","next":"Continue","home_title":"Real people.","home_near":"Real closeness.","home_lead":"Dating without inactive profiles, hidden costs or artificial chats. Find people near you who clearly say what they are looking for.","start":"Start for free","why":"Why SaMaWi?","card":"Dating, as it should be.","rows":["Local search instead of district chaos","Clear intentions and real activity","Messages without credits per message","Anti-scam protection from the start","18+ and privacy by design"],"reg_intro":"The first step to your profile.","adult":"SaMaWi Dating is exclusively for adults aged 18+. Your date of birth is checked server-side."},
    "fr": {"login":"Connexion","register":"Inscription gratuite","email":"Adresse e-mail","password":"Mot de passe","submit":"Se connecter","title":"Bon retour","bad":"L’e-mail ou le mot de passe est incorrect.","inactive":"Veuillez d’abord confirmer votre adresse e-mail.","birth":"Date de naissance","create":"Créer un compte","next":"Continuer","home_title":"De vraies personnes.","home_near":"Une vraie proximité.","home_lead":"Des rencontres sans profils fantômes, coûts cachés ni chats artificiels. Trouve des personnes près de chez toi qui disent clairement ce qu’elles recherchent.","start":"Commencer gratuitement","why":"Pourquoi SaMaWi ?","card":"Les rencontres comme elles devraient être.","rows":["Recherche locale plutôt que chaos administratif","Intentions claires et activité réelle","Messages sans crédits par message","Protection anti-arnaque dès le départ","18+ et confidentialité dès la conception"],"reg_intro":"La première étape vers ton profil.","adult":"SaMaWi Dating est exclusivement réservé aux adultes de 18 ans et plus. Ta date de naissance est vérifiée côté serveur."},
    "it": {"login":"Accedi","register":"Registrati gratis","email":"Indirizzo e-mail","password":"Password","submit":"Accedi","title":"Bentornato","bad":"E-mail o password non corretti.","inactive":"Conferma prima il tuo indirizzo e-mail.","birth":"Data di nascita","create":"Crea account","next":"Continua","home_title":"Persone vere.","home_near":"Vera vicinanza.","home_lead":"Dating senza profili fantasma, costi nascosti o chat artificiali. Trova persone vicino a te che dicono chiaramente cosa cercano.","start":"Inizia gratis","why":"Perché SaMaWi?","card":"Dating, come dovrebbe essere.","rows":["Ricerca locale invece del caos dei distretti","Intenzioni chiare e attività reale","Messaggi senza crediti per messaggio","Protezione anti-truffa fin dall’inizio","18+ e privacy by design"],"reg_intro":"Il primo passo verso il tuo profilo.","adult":"SaMaWi Dating è riservato esclusivamente agli adulti dai 18 anni in su. La data di nascita viene verificata sul server."},
}

COMMON_CSS = """*{box-sizing:border-box}body{margin:0;padding-top:72px;font-family:system-ui,-apple-system,sans-serif;background:#101114;color:#f6f6f6}.top{position:fixed;z-index:100;top:0;left:0;right:0;height:72px;background:#101114ef;backdrop-filter:blur(10px);display:flex;align-items:center;justify-content:space-between;padding:0 max(24px,calc((100vw - 1120px)/2));border-bottom:1px solid #17191e}.brand{font-size:24px;font-weight:800;color:#fff;text-decoration:none}.brand span{color:#ff5c72}.navright{display:flex;gap:14px;align-items:center}.top a{color:#fff;text-decoration:none}.top .cta{background:#ff5c72;padding:10px 16px;border-radius:999px;font-weight:700}.language-picker{display:flex;align-items:center;gap:6px;color:#aaa}.language-picker select{width:112px;background:#17191e;color:#fff;border:1px solid #343740;border-radius:9px;padding:8px 28px 8px 9px}.authlinks{display:flex;align-items:center;gap:14px;white-space:nowrap}.navright{margin-left:auto;justify-content:flex-end;min-width:430px}@media(max-width:700px){.navright{gap:8px;min-width:0}.language-picker span{display:none}.language-picker select{width:70px}.top .cta{padding:9px 12px}.brand{font-size:20px}.authlinks{gap:8px}}"""

def lang_for(request: Request) -> str:
    q = request.query_params.get("lang", "").lower()
    if q in LANGS: return q
    cookie = request.cookies.get("lang", "").lower()
    if cookie in LANGS: return cookie
    accept = request.headers.get("accept-language", "").lower()
    for code in ("de","fr","it","en"):
        if code in accept: return code
    return "en"

def header_html(lang: str, logged_in: bool = False, path: str = "/") -> str:
    t=LANGS[lang]
    auth = '<a href="/logout">Logout</a>' if logged_in else f'<a href="/login?lang={lang}">{t["login"]}</a><a class="cta" href="/register?lang={lang}">{t["register"]}</a>'
    available = [("de","Deutsch"),("en","English"),("fr","Français"),("it","Italiano")]
    planned = ["Español","Português","Nederlands","Polski","Čeština","Magyar","Română","Ελληνικά","Türkçe","Українська","Русский","中文（简体）","中文（繁體）","日本語","한국어"]
    options = "".join(f'<option value="{code}"{" selected" if code==lang else ""}>{label}</option>' for code,label in available)
    options += '<optgroup label="Coming soon">' + "".join(f'<option disabled>{label}</option>' for label in planned) + '</optgroup>'
    selector = f'<label class="language-picker" aria-label="Language"><span>🌐</span><select onchange="location.href=\'{path}?lang=\'+this.value">{options}</select></label>'
    return f'<nav class="top"><a class="brand" href="/?lang={lang}">SaMaWi<span>.</span>dating</a><div class="navright">{selector}<span class="authlinks">{auth}</span></div></nav>'

def page_response(html: str, lang: str, status_code: int = 200) -> HTMLResponse:
    r=HTMLResponse(html,status_code=status_code)
    r.set_cookie("lang",lang,max_age=31536000,secure=True,samesite="lax",path="/")
    return r

def home_page(lang: str) -> str:
    t=LANGS[lang]; rows="".join(f'<div class="row"><span class="check">✓</span>{x}</div>' for x in t["rows"])
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SaMaWi Dating</title><style>{COMMON_CSS}main{{max-width:1120px;margin:auto;padding:90px 24px 70px;display:grid;grid-template-columns:1.15fr .85fr;gap:70px;align-items:center}}h1{{font-size:clamp(46px,7vw,78px);line-height:.98;margin:0 0 25px}}h1 em{{font-style:normal;color:#ff5c72}}.lead{{font-size:20px;line-height:1.6;color:#c9cbd1;max-width:650px}}.actions{{margin-top:34px;display:flex;gap:14px;flex-wrap:wrap}}.button{{display:inline-block;padding:15px 24px;border-radius:999px;text-decoration:none;font-weight:800}}.primary{{background:#ff5c72;color:white}}.secondary{{border:1px solid #4a4d55;color:white}}.card{{background:#1b1d22;border:1px solid #30333b;border-radius:28px;padding:32px;box-shadow:0 30px 80px #0008}}.card h2{{margin-top:0;font-size:28px}}.row{{padding:15px 0;border-bottom:1px solid #30333b}}.row:last-child{{border:0}}.check{{color:#67dda0;font-weight:800;margin-right:10px}}footer{{text-align:center;color:#777;padding:40px 20px}}@media(max-width:800px){{main{{grid-template-columns:1fr;padding-top:45px}}}}</style></head><body>{header_html(lang,path="/")}<main><section><h1>{t["home_title"]}<br><em>{t["home_near"]}</em></h1><p class="lead">{t["home_lead"]}</p><div class="actions"><a class="button primary" href="/register?lang={lang}">{t["start"]}</a><a class="button secondary" href="#why">{t["why"]}</a></div></section><section class="card" id="why"><h2>{t["card"]}</h2>{rows}</section></main><footer>© 2026 SaMaWi Dating · dating.samawi.co.uk</footer></body></html>'''

def register_page(lang: str) -> str:
    t=LANGS[lang]
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{t["create"]} · SaMaWi Dating</title><script src="https://challenges.cloudflare.com/turnstile/v0/api.js" async defer></script><style>{COMMON_CSS}.box{{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}}label{{display:block;margin:18px 0 7px;color:#c9cbd1}}input{{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font-size:16px}}button{{width:100%;margin-top:25px;padding:15px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}}.note{{color:#92959d;font-size:14px;line-height:1.5}}</style></head><body>{header_html(lang,path="/register")}<main class="box"><h1>{t["create"]}</h1><p>{t["reg_intro"]}</p><form method="post" action="/api/register?lang={lang}"><label>{t["email"]}</label><input name="email" type="email" required autocomplete="email"><label>{t["birth"]}</label><input name="birth_date" type="date" required><label>{t["password"]}</label><input name="password" type="password" minlength="10" required autocomplete="new-password"><div style="margin-top:22px" class="cf-turnstile" data-sitekey="0x4AAAAAAFHp5Nw6yg0wNLfG" data-action="register" data-theme="dark"></div><button>{t["next"]}</button></form><p class="note">{t["adult"]}</p></main></body></html>'''

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
<style>{COMMON_CSS}.box{{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}}label{{display:block;margin:18px 0 7px;color:#c9cbd1}}input{{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font-size:16px}}button{{width:100%;margin-top:25px;padding:15px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}}.err{{color:#ff8293}}@media(max-width:700px){{.lang{{display:none}}}}</style></head><body>{header_html(lang, path='/login')}<main class="box"><h1>{t["title"]}</h1>{err}<form method="post" action="/api/login?lang={lang}"><label>{t["email"]}</label><input name="email" type="email" required autocomplete="email"><label>{t["password"]}</label><input name="password" type="password" required autocomplete="current-password"><button>{t["submit"]}</button></form></main></body></html>'''

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
    response=HTMLResponse("",status_code=303,headers={"Location":"/profile/setup?lang="+lang})
    response.set_cookie("samawi_session",token,max_age=2592000,httponly=True,secure=True,samesite="lax",path="/")
    response.set_cookie("lang",lang,max_age=31536000,secure=True,samesite="lax",path="/")
    return response

@app.get("/logout")
async def logout(request: Request):
    token=request.cookies.get("samawi_session","")
    if token:
        await request.scope["env"].DB.prepare("DELETE FROM sessions WHERE token = ?").bind(token).run()
    response=HTMLResponse("",status_code=303,headers={"Location":"/"})
    response.delete_cookie("samawi_session",path="/")
    return response

@app.get("/profile/setup", response_class=HTMLResponse)
async def profile_setup(request: Request):
    lang=lang_for(request)
    token=request.cookies.get("samawi_session","")
    row=None
    if token:
        row=await request.scope["env"].DB.prepare("SELECT s.user_id,p.user_id AS profile_id,p.display_name,p.bio,p.locality FROM sessions s LEFT JOIN profiles p ON p.user_id=s.user_id WHERE s.token=? AND s.expires_at > datetime('now') LIMIT 1").bind(token).first()
    if not row:
        return HTMLResponse("",status_code=303,headers={"Location":"/login?lang="+lang})
    labels={
      "de":("Dein Profil","Anzeigename","Über mich","Ort / Region","Suchradius","Was suchst du?","Speichern","Dein genauer Standort wird nicht öffentlich angezeigt."),
      "en":("Your profile","Display name","About me","Town / region","Search radius","What are you looking for?","Save","Your exact location is never shown publicly."),
      "fr":("Ton profil","Nom affiché","À propos de moi","Ville / région","Rayon de recherche","Que recherches-tu ?","Enregistrer","Ta position exacte n’est jamais affichée publiquement."),
      "it":("Il tuo profilo","Nome visualizzato","Su di me","Città / regione","Raggio di ricerca","Cosa cerchi?","Salva","La tua posizione esatta non viene mai mostrata pubblicamente.")
    }[lang]
    intentions={"de":["Beziehung","Dating","Freundschaft","Aktivitäten","Friends+","Abenteuer"],"en":["Relationship","Dating","Friendship","Activities","Friends+","Adventure"],"fr":["Relation","Rencontres","Amitié","Activités","Friends+","Aventure"],"it":["Relazione","Dating","Amicizia","Attività","Friends+","Avventura"]}[lang]
    saved=await request.scope["env"].DB.prepare("SELECT intention_code FROM profile_intentions WHERE user_id=?").bind(str(row.user_id)).all()
    selected={str(x.intention_code) for x in saved.results}
    codes=["relationship","dating","friendship","activities","friends_plus","adventure"]
    checks="".join(f'<label class="choice"><input type="checkbox" name="intentions" value="{codes[i]}"{" checked" if codes[i] in selected else ""}> {x}</label>' for i,x in enumerate(intentions))
    current_name=str(row.display_name or "").replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;")
    current_bio=str(row.bio or "").replace("&","&amp;").replace("<","&lt;")
    current_location=str(row.locality or "").replace("&","&amp;").replace('"',"&quot;").replace("<","&lt;")
    return page_response(f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{labels[0]} · SaMaWi Dating</title><style>{COMMON_CSS}.wrap{{max-width:820px;margin:55px auto;padding:0 24px 70px}}.card{{background:#1b1d22;border:1px solid #30333b;border-radius:26px;padding:34px}}h1{{margin-top:0}}label.field{{display:block;margin:20px 0 8px;color:#c9cbd1}}input[type=text],input[type=number],textarea{{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font:inherit}}textarea{{min-height:130px;resize:vertical}}.choices{{display:flex;flex-wrap:wrap;gap:10px}}.choice{{border:1px solid #454954;border-radius:999px;padding:10px 14px;background:#111318}}button{{margin-top:28px;padding:14px 26px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}}.note{{color:#92959d;font-size:14px}}</style></head><body>{header_html(lang,True,path='/profile/setup')}<main class="wrap"><section class="card"><h1>{labels[0]}</h1><form method="post" action="/api/profile?lang={lang}"><label class="field">{labels[1]}</label><input type="text" name="display_name" maxlength="60" value="{current_name}" required><label class="field">{labels[2]}</label><textarea name="bio" maxlength="1500">{current_bio}</textarea><label class="field">{labels[3]}</label><input type="text" name="location_label" maxlength="100" value="{current_location}" required><p class="note">{labels[7]}</p><label class="field">{labels[4]} (km)</label><input type="number" name="radius_km" min="1" max="500" value="50" required><label class="field">{labels[5]}</label><div class="choices">{checks}</div><button>{labels[6]}</button></form></section></main></body></html>''',lang)

@app.post("/api/profile")
async def save_profile(request: Request):
    lang=lang_for(request)
    token=request.cookies.get("samawi_session","")
    session=None
    if token:
        session=await request.scope["env"].DB.prepare("SELECT user_id FROM sessions WHERE token=? AND expires_at > datetime('now') LIMIT 1").bind(token).first()
    if not session:
        return HTMLResponse("",status_code=303,headers={"Location":"/login?lang="+lang})
    parsed=urllib.parse.parse_qs((await request.body()).decode("utf-8"),keep_blank_values=True)
    name=str(parsed.get("display_name",[""])[0]).strip()
    bio=str(parsed.get("bio",[""])[0]).strip()
    location=str(parsed.get("location_label",[""])[0]).strip()
    try: radius=max(1,min(500,int(parsed.get("radius_km",["50"])[0])))
    except: radius=50
    if not name or not location:
        return HTMLResponse("Missing profile data",status_code=400)
    env=request.scope["env"]; uid=str(session.user_id)
    await env.DB.prepare("INSERT INTO profiles (user_id,display_name,bio,locality) VALUES (?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET display_name=excluded.display_name,bio=excluded.bio,locality=excluded.locality").bind(uid,name,bio,location).run()
    await env.DB.prepare("DELETE FROM profile_intentions WHERE user_id=?").bind(uid).run()
    for code in parsed.get("intentions",[]):
        if code in ("relationship","dating","friendship","activities","friends_plus","adventure"):
            await env.DB.prepare("INSERT OR IGNORE INTO profile_intentions (user_id,intention_code) VALUES (?,?)").bind(uid,code).run()
    return HTMLResponse("",status_code=303,headers={"Location":"/profile/setup?lang="+lang})

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    lang=lang_for(request)
    return page_response(home_page(lang),lang)

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    lang=lang_for(request)
    return page_response(register_page(lang),lang)

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
