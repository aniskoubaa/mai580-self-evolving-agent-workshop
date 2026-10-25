# Improve the Agent—and Defend Your Decision

A hands-on MAI580 workshop on self-evolving agents, technical reasoning, teamwork,
peer review, and communication.

**Prof. Anis Koubaa · Alfaisal University · Fall 2026**

A small phone-insurance agent changes its prompt, harness, or enabled tools—one
component per generation. A meta-model proposes changes after inspecting mistakes.
An acceptance gate keeps a candidate only when its practice score improves.

> **Workshop tasks are in [`v2/`](v2/).** Version 2 is the same agent, split into
> small classes with one idea per folder, plus three tasks with unit tests. Start
> with [`v2/README.md`](v2/README.md). `evolve.py` below is the single-script
> version shown in the Topic 8A video.

## Start here

You need Python 3.10 or later. The demo uses the Python standard library; no packages
need to be installed. The recorded replay requires no API key or internet connection
after cloning.

```bash
git clone https://github.com/aniskoubaa/mai580-self-evolving-agent-workshop.git
cd mai580-self-evolving-agent-workshop
python3 evolve.py --step
```

Press Enter to move between screens. Alternatively:

```bash
python3 evolve.py          # replay the complete demonstration
python3 evolve.py --reset  # remove generated versions and response cache
```

Each run starts at `agents/v0.json`. Reset removes generated `v1`, `v2`, etc.; it
does not overwrite edits you make to `v0.json`. Restore that file with
`git restore agents/v0.json` if needed.

## Before class

1. Watch the recorded Topic 8A practical demonstration shared by the instructor.
2. Clone this repository and run the recorded demo.
3. Read `agents/v0.json` and the three policy rules below.
4. Bring your laptop and one question about a failure or evaluation decision.

Then follow [WORKSHOP.md](WORKSHOP.md). Record your evidence in
[TEAM_REPORT.md](TEAM_REPORT.md).

## The task

The agent approves or denies fictional phone-insurance claims using three rules:

1. Damage and theft are covered; a lost phone is not covered.
2. Theft requires a police report.
3. The claim must be reported at most 30 days after the incident.

| Component | What changes | Starting point |
|---|---|---|
| Prompt | Instructions given to the model | Two lines without the policy rules |
| Harness | Which claim fields the model receives | Description only |
| Tools | Functions run by the harness | No enabled tools |

The model does not autonomously call tools: the harness runs the enabled functions
and supplies their results. The meta-model chooses among these predefined options;
it does not rewrite arbitrary Python code or change model weights.

## What the recorded run shows

| Version | Change | Practice score |
|---|---|---|
| v0 | Starting agent | 6/10 |
| v1 | Add policy rules to the prompt | 7/10 |
| v2 | Supply cause, dates, and police-report information | 8/10 |
| v3 | Enable exact date arithmetic | 10/10 |

On five demonstration exam claims, v0 scores 3/5 and v3 scores 5/5.
Some earlier changes also break previously correct answers. Inspect those regressions
alongside the total score.

These are results from one recorded run on a small teaching dataset. The ten practice
claims are reused for proposing and accepting changes, so their score is a development
score. The gate checks only total practice accuracy; it has no separate safety check
or human-approval stage. Designing a stronger gate is part of the workshop.

The five exam claims are excluded from the improvement loop, but their inputs and
labels are public in this repository and appear in the video. They demonstrate a
split; they are not a fresh blind assessment for students. For a new experiment,
another team or the instructor should reserve new claims until the candidate is frozen.

## Replay versus live experiments

Replay uses recorded answers indexed by the exact model request. It supports tracing
the original run. It does not generate answers to newly edited prompts or claims.
A request absent from the recording stops with an explanatory error.

To evaluate new configurations with the models, set `GEMINI_API_KEY` in your shell
environment and run:

```bash
python3 evolve.py --fresh
```

Live runs call the Gemini API and may incur charges. Keep your key outside the
repository. The original model identifiers are `gemini-2.5-flash-lite` and
`gemini-2.5-flash`; live access depends on your account and model availability.
Live runs are optional for class; replay and the recorded-evidence gate exercise
are available without an API key.

## Files

| File | Purpose |
|---|---|
| `evolve.py` | Agent, tool library, meta-model, acceptance loop, and terminal display |
| `agents/v0.json` | Initial configuration |
| `data/claims.json` | Fictional practice and demonstration exam claims with labels |
| `data/recorded_run.json` | Recorded model responses for offline replay |
| `WORKSHOP.md` | Team activities and peer-review questions |
| `TEAM_REPORT.md` | Evidence and decision template |

Adapted from the [MAI580 course repository](https://github.com/aniskoubaa/mai580_agentic_ai),
Topic 8A. Code is MIT licensed; teaching materials are CC BY-NC-SA 4.0.
See [LICENSE](LICENSE).
