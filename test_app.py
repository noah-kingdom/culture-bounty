import app

def fake_qget(key,path,params):
    if path == "/search":
        return {"results":[{"name":"Patagonia","entity_id":"brand-1"}]}
    kind = params["filter.type"].split(":")[-1]
    longtail = params.get("filter.popularity.max") is not None
    prefix = ("Long " if longtail else "") + kind.title()
    return {"results":{"entities":[
        {"name":f"{prefix} {i}","query":{"affinity":0.9-i*0.05,"explainability":{"brand-1":0.8-i*0.03}}}
        for i in range(1,9)
    ]}}

orig = app.qget
app.qget = fake_qget
try:
    r = app.run_agent("fake","Patagonia","Test objective")
    assert r["brand"] == "Patagonia"
    assert len(r["domains"]["podcast"]) == 6
    assert len(r["longtail"]) == 6
    assert r["brief"]["partner"].startswith("Long Podcast")
    assert any(step[0] == "DIVERSIFY" for step in r["trace"])
    assert any(step[0] == "BRIEF" for step in r["trace"])
    assert r["delta"]["novel_count"] == 5
    out = app.result_page(r)
    assert "QLOO DELTA" in out
    assert "AGENT TRACE" in out
    assert "BOUNTY BRIEF" in out
    assert "LONG-TAIL SCOUT" in out
    print("V0_2_AGENT_TESTS_PASS")
finally:
    app.qget = orig
