#!/usr/bin/env python3
"""Load a generated ?ctz= URL in real Chrome (live falstad.com build), via the DevTools protocol:
records labeled-node voltages every frame through CircuitJS1.onupdate, checks the loaded element count,
and saves a screenshot. Usage: falstad_live_check.py <name> <seconds> <node1,node2,...>"""
import json, os, subprocess, sys, time, urllib.request, base64, websocket
HERE = os.path.dirname(os.path.abspath(__file__))
name, secs, nodes = sys.argv[1], float(sys.argv[2]), sys.argv[3].split(",")
url = open(os.path.join(HERE, name + ".url")).read().strip()
port = 9333
prof = f"/tmp/falstad_prof_{os.getpid()}"
chrome = subprocess.Popen(["google-chrome", f"--remote-debugging-port={port}", f"--user-data-dir={prof}", "--no-first-run",
                           "--no-default-browser-check", "--window-size=1500,1000", "--disable-background-timer-throttling",
                           "--disable-renderer-backgrounding", "--disable-backgrounding-occluded-windows", "about:blank"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=dict(os.environ))
try:
    for _ in range(50):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.2)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, timeout=60, suppress_origin=True); mid = [0]
    def call(method, **params):
        mid[0] += 1; ws.send(json.dumps({"id": mid[0], "method": method, "params": params}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == mid[0]: return m.get("result", m)
    def ev(expr):
        r = call("Runtime.evaluate", expression=expr, returnByValue=True)
        return r.get("result", {}).get("value")
    call("Page.enable"); call("Page.navigate", url=url)
    for _ in range(100):
        time.sleep(0.3)
        if ev("typeof window.CircuitJS1 !== 'undefined' && CircuitJS1.getElements().length > 0"): break
    nel = ev("CircuitJS1.getElements().length")
    ev("window.__rec=[]; CircuitJS1.onupdate=function(c){window.__rec.push([c.getTime()].concat(%s.map(n=>c.getNodeVoltage(n))));};" % json.dumps(nodes))
    time.sleep(secs)
    rec = ev("window.__rec")
    shot = call("Page.captureScreenshot", format="png")
    open(os.path.join(HERE, "shots", name + "_live.png"), "wb").write(base64.b64decode(shot["data"]))
    out = dict(name=name, loaded_elements=nel, frames=len(rec or []), sim_time_s=rec[-1][0] if rec else None,
               timestep=ev("CircuitJS1.getMaxTimeStep()"), nodes=nodes)
    json.dump(dict(out, rec=rec), open(os.path.join(HERE, "shots", name + "_live.json"), "w"))
    print(json.dumps(out))
finally:
    chrome.terminate()
