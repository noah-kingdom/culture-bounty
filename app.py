from __future__ import annotations
import html, json, os, re, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse
import requests

HOST = "https://hackathon.api.qloo.com"
PORT = int(os.getenv("PORT", "8088"))
FROZEN = {
    "Patagonia": ["The Dirtbag Diaries", "Outside Podcast", "How I Built This"],
    "Aesop": ["Articles of Interest", "99% Invisible", "The Business of Fashion Podcast"],
    "Liquid Death": ["The Joe Rogan Experience", "Conan O'Brien Needs a Friend", "Armchair Expert"],
}
DOMAINS = [
    ("podcast", "Podcasts"),
    ("artist", "Artists"),
    ("movie", "Movies"),
    ("destination", "Destinations"),
]

def norm(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())

def entities(payload):
    r = payload.get("results")
    if isinstance(r, list):
        return r
    if isinstance(r, dict) and isinstance(r.get("entities"), list):
        return r["entities"]
    return payload.get("entities", []) if isinstance(payload.get("entities"), list) else []

def ename(e):
    return str(e.get("name") or e.get("title") or e.get("properties", {}).get("name") or "")

def eid(e):
    return str(e.get("entity_id") or e.get("id") or e.get("uuid") or "")

def explainability(e):
    q = e.get("query", {}) if isinstance(e, dict) else {}
    x = q.get("explainability")
    if not x:
        return None
    return x

def affinity(e):
    q = e.get("query", {}) if isinstance(e, dict) else {}
    for v in (q.get("affinity"), e.get("affinity"), e.get("score")):
        try:
            f = float(v)
            if 0 <= f <= 1:
                return f
        except (TypeError, ValueError):
            pass
    return None

def short_explain(x):
    if not x:
        return "Qloo explainability unavailable for this result."
    warning = x.get("warning") if isinstance(x, dict) else None
    if warning:
        return "Qloo returned a recommendation but could not compute full explainability."
    return "Qloo traced this recommendation back to the brand taste signal."

def qget(key, path, params):
    r = requests.get(
        HOST + path,
        headers={"X-Api-Key": key, "accept": "application/json"},
        params=params,
        timeout=25,
    )
    if r.status_code >= 400:
        raise RuntimeError(f"Qloo HTTP {r.status_code}: {r.text[:600]}")
    return r.json()

def resolve_brand(key, brand):
    raw = qget(key, "/search", {
        "query": brand,
        "types": "urn:entity:brand",
        "take": 10,
        "sort_by": "match",
    })
    xs = entities(raw)
    exact = [x for x in xs if norm(ename(x)) == norm(brand)]
    x = (exact or xs)[0] if xs else None
    if not x or not eid(x):
        raise RuntimeError("Qloo could not resolve that brand.")
    return x

def insights(key, brand_id, kind, longtail=False, take=8):
    p = {
        "filter.type": f"urn:entity:{kind}",
        "signal.interests.entities": brand_id,
        "feature.explainability": "true",
        "take": take,
    }
    if kind != "destination":
        p["bias.trends"] = "low"
    if longtail and kind == "podcast":
        p["filter.popularity.max"] = 0.80
    return qget(key, "/v2/insights", p)

def pack_results(payload, limit=6):
    out = []
    for i, e in enumerate(entities(payload), 1):
        n = ename(e)
        if not n:
            continue
        out.append({
            "rank": i,
            "name": n,
            "affinity": affinity(e),
            "explainability": explainability(e),
            "explain_text": short_explain(explainability(e)),
        })
        if len(out) >= limit:
            break
    return out

def run_agent(key, brand, objective):
    trace = []
    t0 = time.time()
    b = resolve_brand(key, brand)
    trace.append(("RESOLVE", f"Matched '{brand}' to Qloo entity {eid(b)[:8]}…"))

    domains = {}
    for kind, label in DOMAINS:
        domains[kind] = pack_results(insights(key, eid(b), kind))
        trace.append(("EXPLORE", f"Scouted {label.lower()} through Qloo taste graph."))

    longtail = pack_results(insights(key, eid(b), "podcast", longtail=True))
    trace.append(("DIVERSIFY", "Re-ran podcast search with popularity capped at 0.80."))

    frozen = FROZEN.get(brand)
    delta = None
    if frozen:
        top5 = [x["name"] for x in domains["podcast"][:5]]
        fset = {norm(x) for x in frozen}
        novel = [x for x in top5 if norm(x) not in fset]
        delta = {"baseline": frozen, "qloo": top5, "novel": novel, "novel_count": len(novel)}
        trace.append(("COMPARE", f"Qloo produced {len(novel)}/5 podcast candidates outside frozen LLM baseline."))

    candidate = (longtail or domains["podcast"])[0] if (longtail or domains["podcast"]) else None
    if not candidate:
        raise RuntimeError("Qloo returned no podcast candidates.")
    trace.append(("SELECT", f"Selected #{candidate['rank']} long-tail cultural bridge: {candidate['name']}."))

    brief = {
        "brand": ename(b),
        "objective": objective or "Reach a culturally aligned audience without defaulting to obvious influencer picks.",
        "partner": candidate["name"],
        "offer": "$200 verified placement bounty",
        "rule": "AUTHORIZE → verify placement → CAPTURE; otherwise VOID",
        "why": candidate["explain_text"],
    }
    trace.append(("BRIEF", "Generated a fail-closed bounty brief for human approval."))
    trace.append(("DONE", f"Agent completed in {time.time()-t0:.2f}s."))

    return {
        "brand": ename(b),
        "brand_id": eid(b),
        "objective": objective,
        "domains": domains,
        "longtail": longtail,
        "delta": delta,
        "brief": brief,
        "trace": trace,
    }

def esc(x):
    return html.escape(str(x))

CSS = """
:root{--bg:#090b10;--panel:#121722;--muted:#98a2b3;--line:#273142;--hot:#f5f7fa}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 15% 0,#182238 0,#090b10 40%);color:var(--hot);font-family:Inter,ui-sans-serif,system-ui,-apple-system,Segoe UI,sans-serif}
.w{max-width:1180px;margin:auto;padding:42px 24px 80px}.eyebrow{font-size:12px;letter-spacing:.18em;color:#9fb5ff;text-transform:uppercase}.hero{font-size:58px;line-height:.94;margin:12px 0 18px;max-width:850px}.lead{font-size:18px;line-height:1.6;color:#b7c0cf;max-width:820px}
.grid{display:grid;grid-template-columns:1.1fr .9fr;gap:18px}.panel{background:rgba(18,23,34,.93);border:1px solid var(--line);border-radius:20px;padding:22px;box-shadow:0 18px 60px rgba(0,0,0,.25)}
input,select{width:100%;background:#0b1018;color:#fff;border:1px solid #344155;border-radius:12px;padding:13px;margin:7px 0 15px;font:inherit}button{background:#f5f7fa;color:#111827;border:0;border-radius:12px;padding:13px 18px;font-weight:800;cursor:pointer}
.badge{display:inline-flex;padding:7px 10px;border:1px solid #344155;border-radius:999px;font-size:12px;color:#c8d1df}.ok{border-color:#356e55;color:#a7f3d0}.warn{border-color:#7a5d27;color:#fde68a}
.steps{display:flex;gap:8px;flex-wrap:wrap}.step{padding:8px 10px;border:1px solid #2c384b;border-radius:10px;color:#b9c5d7;font-size:12px}.row{padding:12px 0;border-top:1px solid #253044}.rank{color:#7385a0;font-size:12px}.name{font-weight:750}.why{color:#9da9ba;font-size:13px;margin-top:5px}.bar{height:5px;background:#202a39;border-radius:999px;margin-top:8px;overflow:hidden}.fill{height:100%;background:#dbe5ff}.tabs{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.domain h3{margin:0 0 8px}.domain{min-width:0}.delta{display:grid;grid-template-columns:1fr 1fr;gap:14px}.list{margin:0;padding-left:20px;color:#c5cfdd}.brief{border:1px solid #395877;background:linear-gradient(135deg,#121b2b,#151822)}.trace{font-family:ui-monospace,SFMono-Regular,Consolas,monospace;font-size:12px;color:#aab6c8}.trace div{padding:7px 0;border-bottom:1px dashed #273142}
small{color:var(--muted)}a{color:#c9d7ff}@media(max-width:850px){.grid,.tabs,.delta{grid-template-columns:1fr}.hero{font-size:42px}}
"""

def layout(body):
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>CULTURE//BOUNTY</title><style>{CSS}</style></head><body><main class='w'>{body}</main></body></html>"

def home(error=""):
    secret_note = "Server key detected; judges can run without entering a credential." if os.getenv("QLOO_API_KEY") else "Local mode: paste your Qloo key. It is used for this request only and is not stored."
    err = f"<div class='panel warn'><b>Run failed</b><p>{esc(error)}</p></div>" if error else ""
    return layout(f"""
<div class='eyebrow'>Qloo Agentic Hackathon · Cultural Intelligence Agent</div>
<h1 class='hero'>Find the cultural bridge<br>an LLM would miss.</h1>
<p class='lead'>CULTURE//BOUNTY turns a brand into a cross-domain taste map, deliberately hunts the long tail, explains the cultural signal, and creates a verified creator-placement bounty brief.</p>
<div class='steps'><span class='step'>1 Resolve</span><span class='step'>2 Explore</span><span class='step'>3 Diversify</span><span class='step'>4 Explain</span><span class='step'>5 Select</span><span class='step'>6 Brief</span></div>
{err}
<div class='grid' style='margin-top:22px'>
<form class='panel' method='post' action='/run'>
<label>Brand</label><input name='brand' value='Patagonia' required>
<label>Campaign objective</label><input name='objective' value='Reach adjacent culture without choosing the obvious influencer.'>
{"" if os.getenv("QLOO_API_KEY") else "<label>Qloo API key</label><input type='password' name='key' required>"}
<button>Run Cultural Scout Agent</button>
<p><small>{esc(secret_note)}</small></p>
</form>
<div class='panel'>
<span class='badge ok'>WHY QLOO MATTERS</span>
<h2>Not a prettier recommendation list.</h2>
<p class='lead' style='font-size:15px'>The agent uses Qloo as its cultural grounding layer, then runs a second low-popularity search to escape obvious celebrity choices. Explainability stays attached to the decision trail.</p>
</div></div>""")

def result_page(r):
    trace = "".join(f"<div><b>{esc(a)}</b> · {esc(b)}</div>" for a,b in r["trace"])
    domain_html = ""
    for kind,label in DOMAINS:
        rows = r["domains"][kind][:5]
        items = "".join(result_row(x) for x in rows)
        domain_html += f"<section class='panel domain'><h3>{esc(label)}</h3>{items or '<small>No result</small>'}</section>"
    lt = "".join(result_row(x) for x in r["longtail"][:5])
    delta = ""
    if r["delta"]:
        d = r["delta"]
        left = "".join(f"<li>{esc(x)}</li>" for x in d["baseline"])
        right = "".join(f"<li>{esc(x)}</li>" for x in d["qloo"])
        delta = f"""<section class='panel'><span class='badge ok'>QLOO DELTA · {d['novel_count']}/5 NOVEL</span><h2>Same brand. Different discovery space.</h2><div class='delta'><div><small>Frozen LLM-only baseline</small><ol class='list'>{left}</ol></div><div><small>Live Qloo top 5</small><ol class='list'>{right}</ol></div></div></section>"""
    b = r["brief"]
    return layout(f"""
<div class='eyebrow'>LIVE AGENT RUN · {esc(r["brand"])}</div><h1 class='hero' style='font-size:48px'>Cultural Scout completed.</h1>
<div class='grid'><section class='panel'><span class='badge ok'>AGENT TRACE</span><div class='trace'>{trace}</div></section>
<section class='panel brief'><span class='badge'>BOUNTY BRIEF</span><h2>{esc(b["partner"])}</h2><p><b>{esc(b["offer"])}</b></p><p>{esc(b["why"])}</p><p><small>{esc(b["rule"])}</small></p></section></div>
<h2 style='margin-top:28px'>Cross-domain taste map</h2><div class='tabs'>{domain_html}</div>
<section class='panel' style='margin-top:18px'><span class='badge'>LONG-TAIL SCOUT · POPULARITY ≤ 0.80</span><h2>Deliberately less obvious podcast partners</h2>{lt}</section>
<div style='margin-top:18px'>{delta}</div>
<p style='margin-top:22px'><a href='/'>← Run another brand</a></p>""")

def result_row(x):
    a = x["affinity"]
    bar = "" if a is None else f"<div class='bar'><div class='fill' style='width:{max(0,min(100,a*100)):.0f}%'></div></div><small>Affinity {a:.3f}</small>"
    detail = ""
    if x["explainability"]:
        raw = esc(json.dumps(x["explainability"], ensure_ascii=False)[:900])
        detail = f"<details><summary><small>Qloo explainability</small></summary><small>{raw}</small></details>"
    return f"<div class='row'><div class='rank'>#{x['rank']}</div><div class='name'>{esc(x['name'])}</div><div class='why'>{esc(x['explain_text'])}</div>{bar}{detail}</div>"

class Handler(BaseHTTPRequestHandler):
    def send_html(self, s, status=200):
        b=s.encode("utf-8"); self.send_response(status); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        if p=="/health":
            b=b'{"status":"ok"}'; self.send_response(200); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b); return
        self.send_html(home())
    def do_POST(self):
        if urlparse(self.path).path!="/run": self.send_html(home("Unknown route"),404); return
        n=int(self.headers.get("Content-Length","0")); f=parse_qs(self.rfile.read(n).decode("utf-8"))
        brand=f.get("brand",[""])[0].strip(); objective=f.get("objective",[""])[0].strip()
        key=(os.getenv("QLOO_API_KEY") or f.get("key",[""])[0]).strip()
        try:
            if not key: raise RuntimeError("QLOO_API_KEY is not configured.")
            self.send_html(result_page(run_agent(key,brand,objective)))
        except Exception as e:
            self.send_html(home(str(e)),400)
    def log_message(self,*args): pass

if __name__=="__main__":
    print(f"CULTURE//BOUNTY V0.2 listening on http://0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0",PORT),Handler).serve_forever()
