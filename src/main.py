from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
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

REGISTER = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Registrieren · SaMaWi Dating</title>
<style>body{font-family:system-ui;background:#101114;color:#fff;margin:0}.box{max-width:520px;margin:70px auto;padding:34px;background:#1b1d22;border:1px solid #30333b;border-radius:25px}h1{margin-top:0}label{display:block;margin:18px 0 7px;color:#c9cbd1}input{width:100%;padding:14px;border-radius:10px;border:1px solid #454954;background:#111318;color:#fff;font-size:16px;box-sizing:border-box}button{width:100%;margin-top:25px;padding:15px;border:0;border-radius:999px;background:#ff5c72;color:#fff;font-weight:800;font-size:16px}.note{color:#92959d;font-size:14px;line-height:1.5}a{color:#ff8293}</style></head>
<body><div class="box"><a href="/">← SaMaWi Dating</a><h1>Konto erstellen</h1><p>Der erste Schritt zu deinem Profil.</p>
<form><label>E-Mail-Adresse</label><input type="email" required autocomplete="email"><label>Geburtsdatum</label><input type="date" required><label>Passwort</label><input type="password" minlength="10" required autocomplete="new-password"><button type="button">Weiter</button></form>
<p class="note">SaMaWi Dating ist ausschließlich für Erwachsene ab 18 Jahren. Die Registrierung wird im nächsten Entwicklungsschritt aktiviert.</p></div></body></html>"""

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
