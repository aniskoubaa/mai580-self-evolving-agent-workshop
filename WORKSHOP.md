# Improve the Agent—and Defend Your Decision

**Central question:** Your agent's score increased. What evidence would convince
another team to accept the change?

Use the same structure as the paper-analysis workshop:

**Problem → Claim → Method → Evidence → Critique → Next step.**

## Team roles

Work in teams of three: developer, evaluator, and presenter. Rotate roles during
the activities. Each person should explain at least one technical decision.

## 1. Diagnose before changing anything

Read the policy, the starting configuration, and `request()` in `evolve.py`.
Predict which claims the agent may mishandle and explain why.

- **Knowledge:** Is a policy rule missing from the prompt?
- **Information:** Does the harness hide a field the model needs?
- **Skill:** Does the model need a reliable calculation?

Pick one failure, state its cause, and propose one component to change. Separate
your prediction from an observed result.

## 2. Trace the recorded experiment

Run `python3 evolve.py --step`. Before revealing each candidate's result, predict
what it will fix and what it might break. Inspect the generated `agents/v*.json` files.

Record the practice score, fixed claims, and broken claims for every accepted version.
Explain why a previously correct answer might have been a lucky guess.

## 3. Make one technical change

Choose one route based on access to live models.

### Route A: No API key—implement a gate over recorded evidence

Find the `if new > old:` decision in `main()`. Propose a stronger rule that also
rejects any candidate that newly approves a claim whose correct label is `DENY`.
Such a claim is an invalid payout under the policy.

Write a small Python function taking the claim records and the old and candidate
answers. Return an accept/reject decision and a reason. Use the original replay's
displayed answers to construct inputs. Run your function against at least two
recorded transitions, including one with a higher score and a regression.

Do this in a separate file, for example `gate_exercise.py`, so you can compare its
decisions with the original replay without changing the replay's execution path.
Explain which useful changes your stricter rule could reject. Discuss incorrect
denials too: avoiding invalid payouts alone is not a complete safety policy.

This is a new gate decision over existing evidence. It is not a new model result.

### Route B: Live models—change one agent component

Save the baseline results, then change only the prompt, harness fields, or enabled
tools. Use a separate copy or branch for your experiment.

`--fresh` runs the full improvement loop, which may introduce additional changes.
For a controlled one-component comparison, use `test()` directly on the baseline
and your candidate rather than attributing the whole loop's result to your edit.
For example, create `candidate.json` with the same structure as `agents/v0.json`, then:

```python
import json
import evolve

evolve.FRESH = True
baseline = json.loads((evolve.HERE / "agents/v0.json").read_text())
candidate = json.loads((evolve.HERE / "candidate.json").read_text())
changed = [part for part in baseline if baseline[part] != candidate[part]]
assert len(changed) == 1, "Change exactly one component."

for label, config in [("baseline", baseline), ("candidate", candidate)]:
    answers = evolve.test(config, evolve.PRACTICE)
    print(label, evolve.score(answers, evolve.PRACTICE), "/", len(evolve.PRACTICE))
    for claim, answer in zip(evolve.PRACTICE, answers):
        print(claim["id"], answer, claim["truth"])
```

Set your API key in the environment before running this file. Compare both versions
on identical claims with the same model and settings. Record regressions, not just
the total score. Treat a single run as preliminary evidence.

## 4. Review another team's evidence

Exchange the code change and report. Ask:

- Is the claimed improvement actually measured?
- Were the baseline and candidate evaluated under comparable conditions?
- Did the change fix a cause or memorize particular claims?
- Were test claims, labels, or results used to choose the change?
- Does a higher score hide an invalid payout or an incorrect denial?
- Does the evidence support the claim beyond these examples?

Give one specific strength, one evidence-based concern, and one feasible next test.
The receiving team should revise its work or explain why it disagrees.

## 5. Defend the decision

Give a short presentation using the six-question structure. Finish with one decision:
**accept for further testing**, **reject**, or **gather more evidence**.

Explain one limitation and the next experiment. A well-supported rejection is a
successful outcome. Each student should be ready to answer a question.

## Deliverables

- One runnable code change and its observed output.
- A completed [TEAM_REPORT.md](TEAM_REPORT.md), including peer feedback and revision.
- A short oral defense of the decision.

Keep any new final test separate. Freeze the candidate before another team or the
instructor reveals those claims. Once their results guide an edit, they become
development evidence and a new final test is needed.
