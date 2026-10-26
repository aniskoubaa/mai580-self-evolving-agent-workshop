#!/usr/bin/env python3
"""MAI 580 T08A, version 2: the self-evolving insurance agent, one idea per folder.

  python3 main.py --step     class mode: press Enter between screens
  python3 main.py            the whole run at once
  python3 main.py --reset    restore defaults: only v0 remains, replay = recorded run
  python3 main.py --fresh    call Gemini for real (needs GEMINI_API_KEY)
  python3 main.py --gate safety   use your SafetyGate (Task 2) instead of ScoreGate

Standard library only. Without --fresh it replays data/recorded_run.json.
"""
import argparse
import os
import pathlib
import sys

from agent import AgentConfig, Harness, LLM, ReplayMissing
from claims import ClaimSet, Policy
from gate import SafetyGate, ScoreGate
from loop.console import Console, G, X
from loop.evolution_loop import EvolutionLoop
from meta_agent import MetaAgent
from tools import ToolLibrary

HERE = pathlib.Path(__file__).parent
DATA = HERE / "data"                        # the claims and the class recording
AGENTS = HERE / "agents"
CACHE = HERE / "cache" / "responses.json"


def reset():
    for f in AGENTS.glob("v*.json"):
        f.unlink()
    AgentConfig.default().save(AGENTS / "v0.json")
    CACHE.unlink(missing_ok=True)
    print(f"{G}Defaults restored:{X} agents/ holds only v0.json, and replay uses the recorded run.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--gens", type=int, default=4)
    parser.add_argument("--gate", choices=["score", "safety"], default="score")
    for flag in ("fresh", "reset", "slow", "step"):
        parser.add_argument(f"--{flag}", action="store_true")
    args = parser.parse_args()
    if args.reset:
        return reset()

    for f in AGENTS.glob("v*.json"):            # each run starts from v0
        if f.name != "v0.json":
            f.unlink()
    if not (AGENTS / "v0.json").exists():
        AgentConfig.default().save(AGENTS / "v0.json")

    # Build the objects, then hand them to the loop.
    claims = ClaimSet.load(DATA / "claims.json")
    policy = Policy()
    tool_library = ToolLibrary()
    llm = LLM(recorded=DATA / "recorded_run.json", cache=CACHE, fresh=args.fresh)
    harness = Harness(tool_library)
    meta_agent = MetaAgent(llm, harness, policy, tool_library)
    gate = SafetyGate() if args.gate == "safety" else ScoreGate()
    console = Console(slow=args.slow, step=args.step)

    loop = EvolutionLoop(claims, policy, harness, llm, meta_agent, gate, console, AGENTS)
    loop.run(start=AgentConfig.load(AGENTS / "v0.json"), generations=args.gens)


if __name__ == "__main__":
    if os.name == "nt":
        os.system("")                              # lets older Windows consoles show the colours
    try:
        sys.stdout.reconfigure(errors="replace")   # a symbol the console cannot show becomes "?"
    except AttributeError:
        pass
    try:
        main()
    except KeyError as e:
        sys.exit(f"Missing {e}: set GEMINI_API_KEY, or run without --fresh to replay the recording.")
    except ReplayMissing:
        sys.exit("The recording has no answer for this request, because the agent or the claims "
                 "were changed.\nTo replay the class run again:  git restore agents/v0.json  "
                 "then  python3 main.py --reset\nTo try your change for real:  python3 main.py --fresh  "
                 "(needs GEMINI_API_KEY)")
