#!/usr/bin/env python3
"""MAI 580 T08A demo: a phone-insurance agent that improves its own prompt, harness and tools.

The agent is one JSON file (agents/v0.json) with three parts:
  prompt   the instructions the model reads
  harness  the code around the model; here: which claim fields it sends to the model
  tools    small functions the harness runs for the model (here: date arithmetic)
Each generation of the loop:
  1 test the current agent on 10 practice claims    2 a bigger model diagnoses the mistakes
  3 it changes ONE part -> candidate               4 test the candidate on the same claims
  5 keep the candidate only if more claims are right, otherwise undo
At the end, 5 exam claims (never used in the loop) check the final agent.

  python3 evolve.py --reset    restore defaults: only v0 remains, replay = recorded run
  python3 evolve.py --step     class mode: press Enter between screens
  python3 evolve.py            the whole run at once
  python3 evolve.py --fresh    call Gemini for real (needs GEMINI_API_KEY)
Standard library only. Without --fresh it replays data/recorded_run.json (no key, no internet).
"""
import argparse, concurrent.futures as cf, datetime as dt, hashlib
import json, os, pathlib, sys, textwrap, time, urllib.request

HERE = pathlib.Path(__file__).parent
AGENTS, CACHE = HERE / "agents", HERE / "cache" / "responses.json"
GOLDEN = HERE / "data" / "recorded_run.json"   # the run shown in class; never overwritten
AGENT_MODEL = "gemini-2.5-flash-lite"   # small model: the agent being improved
META_MODEL = "gemini-2.5-flash"         # bigger model: diagnoses mistakes and proposes changes

# ---------------- the default agent (what --reset restores) ----------------
DEFAULT_AGENT = {
    "prompt": ["You handle phone insurance claims for our customers.",
               "Pay the claim if the phone was really damaged or taken."],
    "harness": {"send_fields": ["description"]},
    "tools": [],
}
PART_FOR = {"knowledge": "prompt", "information": "harness", "skill": "tools"}
FIELDS = ["description", "cause", "incident_date", "reported_date", "police_report"]

# the company policy: the meta-model may read it, the agent knows only its own prompt
POLICY = ["Rule 1: covered causes are damage and theft. A lost phone is not covered.",
          "Rule 2: a theft claim needs a police report.",
          "Rule 3: the claim must be reported at most 30 days after the incident."]

# ---------------- tool library: the agent chooses which tools to enable ----
def days_between(c):
    d = (dt.date.fromisoformat(c["reported_date"]) - dt.date.fromisoformat(c["incident_date"])).days
    return f"days_between(incident_date, reported_date) = {d}"

def currency_convert(c):
    return "currency_convert: this claim has no amount to convert"

TOOLS = {"days_between": (days_between, "exact number of days from the incident to the report"),
         "currency_convert": (currency_convert, "converts an amount of money between currencies")}

# ---------------- Gemini call with a replay cache --------------------------
_src = CACHE if CACHE.exists() else GOLDEN
_cache = json.loads(_src.read_text()) if _src.exists() else {}
FRESH = False

def llm(model, text, temperature=0.0):
    key = hashlib.sha256(f"{model}|{temperature}|{text}".encode()).hexdigest()
    if key in _cache and not FRESH:
        return _cache[key]
    if not FRESH:
        raise RuntimeError(
            "No recorded answer matches this request. Replay supports the original "
            "demo only. Restore the original configuration, or use --fresh with "
            "GEMINI_API_KEY to evaluate changes with live model calls."
        )
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
           f":generateContent?key={os.environ['GEMINI_API_KEY']}")
    body = json.dumps({"contents": [{"parts": [{"text": text}]}],
                       "generationConfig": {"temperature": temperature}}).encode()
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, body, {"Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(req, timeout=120))
            out = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
            _cache[key] = out
            return out
        except Exception:  # rate limit or network: wait and retry
            if attempt == 3: raise
            time.sleep(2 ** attempt * 3)

# ---------------- the harness: turns the agent file into one answer --------
CLAIMS = json.loads((HERE / "data/claims.json").read_text())
PRACTICE = [c for c in CLAIMS if c["set"] == "practice"]
N = len(PRACTICE)
EXAM = [c for c in CLAIMS if c["set"] == "exam"]

def request(cfg, c):
    """The exact text the model receives for claim c."""
    lines = list(cfg["prompt"]) + ["", "Claim:"]
    lines += [f"{f}: {c[f]}" for f in FIELDS if f in cfg["harness"]["send_fields"]]
    if cfg["tools"]:
        lines += ["", "Tool results:"] + [TOOLS[t][0](c) for t in cfg["tools"]]
    return "\n".join(lines + ["", "Answer with one word: APPROVE or DENY."])

def answer(cfg, c):
    a = llm(AGENT_MODEL, request(cfg, c)).upper()
    i, j = a.rfind("APPROVE"), a.rfind("DENY")
    return "?" if i == j == -1 else "APPROVE" if i > j else "DENY"

def test(cfg, claims):
    with cf.ThreadPoolExecutor(8) as ex:
        return list(ex.map(lambda c: answer(cfg, c), claims))

# ---------------- the meta-model: diagnoses and changes ONE part -----------
def propose(cfg, answers, undone):
    fails = [(c, a) for c, a in zip(PRACTICE, answers) if a != c["truth"]]
    shown = "\n".join(f"- {json.dumps({f: c[f] for f in FIELDS})}\n"
                      f"  agent said {a}, correct is {c['truth']} ({c['why']})" for c, a in fails)
    tools = "\n".join(f"- {n}: {d}" for n, (_, d) in TOOLS.items())
    text = f"""You improve a small AI agent that approves or denies phone insurance claims.
Company policy:
{chr(10).join(POLICY)}
The agent has three parts you may change:
- "prompt": the instruction lines the agent reads.
- "harness": {{"send_fields": [...]}} which claim fields the harness sends to the agent.
  Possible fields: {FIELDS}. The agent sees nothing else.
- "tools": tools the harness runs and whose results it shows to the agent. Library:
{tools}
Current agent:
{json.dumps(cfg)}
The agent receives this text for a claim (example):
---
{request(cfg, PRACTICE[0])}
---
Its mistakes on the practice claims (full records, the agent saw only the fields above):
{shown}
Changes already tried and undone (do not repeat): {undone or 'none'}

Diagnose the main cause of the mistakes as ONE kind, and fix the part that kind names:
- knowledge: the prompt does not state a rule the agent needs     -> change the "prompt"
- information: a claim field the agent needs is not sent to it    -> change the "harness"
- skill: the agent has every field it needs but counts or calculates wrongly -> change the "tools"
Change exactly ONE part. Keep the prompt at most 6 short lines. Never name a claim in the prompt.
Reply with JSON only:
{{"diagnosis": "<two short, plain sentences>", "kind": "knowledge|information|skill",
  "new_value": <the new value of that part only>}}"""
    raw = llm(META_MODEL, text, temperature=0.3)
    d = json.loads(raw[raw.find("{"): raw.rfind("}") + 1])
    part, new = PART_FOR[d["kind"]], d["new_value"]
    cand = json.loads(json.dumps(cfg))
    if part == "prompt":
        assert isinstance(new, list) and all(isinstance(s, str) for s in new)
    elif part == "harness":
        new = new if isinstance(new, dict) else {"send_fields": new}
        assert all(f in FIELDS for f in new["send_fields"])
        new = {"send_fields": [f for f in FIELDS if f in new["send_fields"]]}
    else:
        new = [t["name"] if isinstance(t, dict) else t for t in (new if isinstance(new, list) else [new])]
        assert part == "tools" and all(t in TOOLS for t in new)
    cand[part] = new
    return d["diagnosis"], d["kind"], part, cand

# ---------------- display ---------------------------------------------------
G, R, Y, C, B, D, X = "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[1m", "\033[2m", "\033[0m"
SLOW, STEP = 0, False

def say(s="", pause=0.0):
    print(s, flush=True); time.sleep(pause * SLOW)

def step():
    if STEP:
        input(f"\n{D}[Enter] next{X}"); print("\033[H\033[2J\033[3J", end="", flush=True)

def facts(c):
    days = (dt.date.fromisoformat(c["reported_date"]) - dt.date.fromisoformat(c["incident_date"])).days
    report = c["police_report"] if c["cause"] == "theft" else "-"
    truth = c["truth"] + ("" if c["why"] == "ok" else f" ({c['why']})")
    return f" {c['id']:6}{c['name']:8}{c['cause']:8}{days:>8}  {report:8}{truth:19}"

def mark(a, c):
    return f"{a:8}{G + '✓' if a == c['truth'] else R + '✗'}{X}"

def table(claims, cols):
    """cols: list of (version name, answers). One row per claim, one column per version."""
    say(f"{D} {'claim':6}{'who':8}{'cause':8}{'days':>8}  {'report':8}{'correct answer':19}"
        + "".join(f"{n:11}" for n, _ in cols) + X)
    for i, c in enumerate(claims):
        row = facts(c) + "".join(f"{mark(ans[i], c)}  " for _, ans in cols)
        if len(cols) == 2 and cols[0][1][i] != cols[1][1][i]:
            ok = cols[1][1][i] == c["truth"]
            row += f"{G}fixed{X}" if ok else f"{R}broken{X}"
        say(row, 0.25)
    say(f" {'score':{len(facts(claims[0])) - 1}}" + "".join(
        f"{B}{str(score(ans, claims)) + '/' + str(len(claims)):11}{X}" for _, ans in cols))

def show_agent(cfg):
    say(f"  {C}PROMPT {X}  " + f"\n  {' ' * 9}".join(cfg["prompt"]))
    say(f"  {C}HARNESS{X}  sends the model these claim fields: {', '.join(cfg['harness']['send_fields'])}")
    say(f"  {C}TOOLS  {X}  {', '.join(cfg['tools']) or 'none'}")

def show_change(part, old, new):
    say(f"  {C}{part.upper()}{X}")
    if part == "prompt":
        for s in old[part]:
            if s not in new[part]: say(f"  {R}- {s}{X}", 0.2)
        for s in new[part]:
            say(f"  {G}+ {s}{X}" if s not in old[part] else f"    {s}", 0.2)
    elif part == "harness":
        added = [f for f in new[part]["send_fields"] if f not in old[part]["send_fields"]]
        say(f"    sends: {', '.join(old[part]['send_fields'])}  {G}+ {', '.join(added)}{X}")
    else:
        say(f"    tools: {', '.join(old[part]) or 'none'}  ->  {G}{', '.join(new[part])}{X}")

def fixed(a, b):
    """Practice claims wrong in answers a and right in answers b."""
    return [c["id"] for c, x, y in zip(PRACTICE, a, b) if x != c["truth"] == y] or "none"

def score(ans, claims):
    return sum(a == c["truth"] for a, c in zip(ans, claims))

# ---------------- files ------------------------------------------------------
def save_cache():
    CACHE.parent.mkdir(exist_ok=True)
    CACHE.write_text(json.dumps(_cache))

def save(cfg, n):
    (AGENTS / f"v{n}.json").write_text(json.dumps(cfg, indent=1) + "\n")

def reset():
    for f in AGENTS.glob("v*.json"):
        f.unlink()
    save(DEFAULT_AGENT, 0)
    CACHE.unlink(missing_ok=True)
    print(f"{G}Defaults restored:{X} agents/ holds only v0.json, and replay uses the recorded run.")

# ---------------- the improvement loop ----------------------------------------
def main():
    global FRESH, SLOW, STEP
    ap = argparse.ArgumentParser()
    ap.add_argument("--gens", type=int, default=4)
    for f in ("fresh", "reset", "slow", "step"):
        ap.add_argument(f"--{f}", action="store_true")
    a = ap.parse_args()
    if a.reset:
        return reset()
    FRESH, SLOW, STEP = a.fresh, 1.0 if a.slow else 0.0, a.step
    for f in AGENTS.glob("v*.json"):                         # each run starts from v0
        if f.name != "v0.json": f.unlink()
    if not (AGENTS / "v0.json").exists(): save(DEFAULT_AGENT, 0)
    v0 = best = json.loads((AGENTS / "v0.json").read_text())

    say(f"{B}A phone-insurance agent that improves itself{X}\n")
    say(f"{B}The company policy{X} (the agent does not know it yet)")
    for r in POLICY: say(f"  {r}", 0.3)
    say(f"\n{B}The starting agent v0{X} (agents/v0.json)"); show_agent(best)
    say(f"\n{B}What the model receives{X} for claim C1 (built by the harness)")
    for line in request(best, PRACTICE[0]).splitlines():
        say(f"  {D}│{X} {line}")
    step()

    say(f"{B}Test v0 on the {len(PRACTICE)} practice claims{X}\n")
    ans = test(best, PRACTICE)
    table(PRACTICE, [("v0", ans)])
    say(f"\n{D}v0 gets {score(ans, PRACTICE)}/{N} right by guessing: it knows no rules and sees only the description.{X}")
    history, undone, version = [("v0", "start", "-", score(ans, PRACTICE), "-")], [], 0
    save_cache()

    for g in range(1, a.gens + 1):
        if score(ans, PRACTICE) == len(PRACTICE):
            break
        step()
        say(f"{B}━━ Generation {g} ━━{X}   current agent: v{version}, score "
            f"{score(ans, PRACTICE)}/{len(PRACTICE)}\n")
        say(f"{B}1 Mistakes{X}")
        for c, x in zip(PRACTICE, ans):
            if x != c["truth"]:
                say(f"  {c['id']} {c['name']:8} said {x:8} correct answer {c['truth']}"
                    + ("" if c["why"] == "ok" else f" ({c['why']})"), 0.2)
        try:
            diagnosis, kind, part, cand = propose(best, ans, undone)
        except Exception as e:
            say(f"{Y}The meta-model gave an invalid proposal ({e}). Skip.{X}"); continue
        say(f"\n{B}2 Diagnosis{X} (meta-model)")
        say(textwrap.fill(diagnosis, 88, initial_indent="  ", subsequent_indent="  "), 1)
        say(f"  kind of problem: {Y}{kind.upper()}{X}  ->  part to change: {C}{part.upper()}{X}", 1)
        say(f"\n{B}3 Change one part{X} -> candidate v{version + 1}")
        show_change(part, best, cand)
        save_cache()
        step()

        say(f"{B}━━ Generation {g} ━━{X}   candidate v{version + 1}: {part} changed\n")
        say(f"{B}4 Test the candidate on the same {len(PRACTICE)} claims{X}\n")
        cans = test(cand, PRACTICE)
        table(PRACTICE, [(f"v{version}", ans), (f"v{version + 1}", cans)])
        old, new = score(ans, PRACTICE), score(cans, PRACTICE)
        say(f"\n{B}5 Decide{X}")
        if new > old:
            version += 1; save(cand, version)
            best, ans = cand, cans
            say(f"  {G}KEEP v{version}{X}: {new}/{N} is better than {old}/{N}. Saved agents/v{version}.json", 1)
            history.append((f"v{version}", part, kind, new, "KEEP"))
        else:
            say(f"  {R}UNDO{X}: {new}/{N} is not better than {old}/{N}. We stay with v{version}.", 1)
            undone.append(f"{part} set to {json.dumps(cand[part])}: fixed {fixed(ans, cans)}, broke {fixed(cans, ans)}")
            history.append(("-", part, kind, new, "UNDO"))
        if score(ans, PRACTICE) == len(PRACTICE):
            say(f"  All {N} practice claims are right, so the loop stops.")
        save_cache()

    step()
    say(f"{B}Final check: 5 exam claims the loop never saw{X}\n")
    table(EXAM, [("v0", test(v0, EXAM)), (f"v{version}", test(best, EXAM))])
    say(f"\n{B}What changed{X}")
    say(f"{D}  {'version':9}{'part':9}{'problem':13}{'practice':>8}  decision{X}")
    for v, p, k, s, d in history:
        col = G if d == "KEEP" else R if d == "UNDO" else ""
        say(f"  {v:9}{p:9}{k:13}{f'{s}/{N}':>8}  {col}{d}{X}", 0.3)
    say(f"\n{D}Restore the defaults any time: python3 evolve.py --reset{X}")
    save_cache()

if __name__ == "__main__":
    try:
        main()
    except KeyError as e:
        sys.exit(f"Missing {e}: set GEMINI_API_KEY, or run without --fresh to replay the recording.")
