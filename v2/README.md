# Version 2 — the same agent, one idea per folder

Version 1 (`../evolve.py`) is one script. Version 2 does exactly the same thing, but
each idea lives in its own folder, and each file holds one small class. Run both on
the recording and they print the same screens.

```bash
cd v2
python3 main.py --step     # press Enter between screens
python3 main.py            # the whole run at once
python3 main.py --reset    # back to v0 only
```

No packages to install and no API key needed: the recorded class run is replayed
from `data/recorded_run.json`. The `v2/` folder is self-contained:
you can copy it anywhere and it still runs.

## Where each idea lives

| Folder | What it holds | Start reading at |
|---|---|---|
| `claims/` | One claim, the practice/exam split, the company policy | `claim.py` |
| `tools/` | Small functions the harness runs for the model | `tool.py`, then `days_between.py` |
| `agent/` | The agent's three parts, the harness, the model call | `config.py`, then `harness.py` |
| `meta_agent/` | The bigger model that diagnoses mistakes and changes ONE part | `proposal.py` |
| `gate/` | Keep the candidate, or undo the change | `score_gate.py` |
| `loop/` | The five steps of each generation, and the screen display | `evolution_loop.py` |

`main.py` only builds the objects and hands them to the loop. Read it first: it
shows how the pieces connect.

## What to read, and what to skip

Read these files in this order. Each one is short and does one job.

1. `main.py`: how the objects are built and connected
2. `loop/evolution_loop.py`: read `run()` first, since every step there is one method
3. `claims/claim.py`: what a claim contains
4. `agent/config.py` and `agent/harness.py`: the three parts, and the text the model sees
5. `tools/tool.py` and `tools/days_between.py`: before Task 1
6. `gate/gate.py` and `gate/score_gate.py`: before Task 2

You do not need to read these for the tasks. They are plumbing, and each file says
so at the top:

- `agent/llm.py`: calls Gemini, or replays the recording
- `loop/console.py`: colours and column widths
- `meta_agent/meta_agent.py`: read only `propose()`; the rest is one long prompt and
  a JSON check

Two Python features you will meet:

- **`@dataclass`** (in `claim.py`) writes `__init__` for you from the list of fields.
- **`@staticmethod`** (in `config.py`) is a function that belongs to the class, not to
  one object. You call it on the class itself, for example `AgentConfig.default()`.

```
main.py ──> EvolutionLoop ──> Agent ──> Harness ──> Tool
                         ├──> MetaAgent ──> Proposal (a new AgentConfig)
                         └──> AcceptanceGate ──> Decision (keep or undo)
```

## Your tasks

Each task is one file with a `TODO`, and one test that tells you when you are done.

| # | File | What to write | Check |
|---|---|---|---|
| 1 | `tools/police_report_check.py` | A new tool for Rule 2 (theft needs a police report) | `python3 -m unittest tests.test_task1_tool` |
| 2 | `gate/safety_gate.py` | A gate that rejects any candidate that newly approves a claim it should deny | `python3 -m unittest tests.test_task2_gate` |
| 3 | `loop/held_out_exam.py` | An exam that can be opened only once | `python3 -m unittest tests.test_task3_exam` |

Run every test at once with `python3 -m unittest`, **from inside `v2/`**. Run from
anywhere else, it finds no tests ("NO TESTS RAN") or cannot import the code. Before you start, only
`test_replay` passes; the task tests fail with "TASK n".

After Task 2, run the loop with your gate:

```bash
python3 main.py --gate safety
```

Look at generation 1. Did your gate make the same decision as `ScoreGate`? Why?
Then the run stops: the class recording never followed this path, so continuing
needs live model calls (`--fresh`, see the main README).

**Stretch.** Add `PoliceReportCheck()` to the list in `tools/library.py`, then run
`python3 main.py --fresh` with your own key. Does the meta-agent ever choose it?
Replay cannot answer this: adding a tool changes the meta-agent's prompt.

## Rule for every change

Change one thing, run the tests, and write down what you expected before you look
at the result. That record is the evidence you defend in `../TEAM_REPORT.md`.
