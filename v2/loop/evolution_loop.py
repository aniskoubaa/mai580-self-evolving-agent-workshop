"""EvolutionLoop — the improvement loop.

Responsibility: run the generations. Each generation has five steps, and each
step is one method below:

    1 show_mistakes()   list the current agent's wrong answers
    2 diagnose()        the meta-agent finds the cause and proposes ONE change
    3 show_change()     show the candidate: the agent with that one part changed
    4 test_candidate()  test the candidate on the same practice claims
    5 decide()          the gate keeps the candidate, or undoes the change

At the end, final_check() tests the first and the final agent on the exam claims.
"""
import json
import textwrap

from agent import Agent, ReplayMissing
from loop.console import B, C, D, G, R, X, Y
from loop.evaluation import fixed_ids, score


class EvolutionLoop:
    def __init__(self, claims, policy, harness, llm, meta_agent, gate, console, agents_dir):
        self.claims = claims
        self.practice = claims.practice
        self.policy = policy
        self.harness = harness
        self.llm = llm
        self.meta_agent = meta_agent
        self.gate = gate
        self.console = console
        self.say = console.say
        self.agents_dir = agents_dir

        # The state of the loop. It changes every time the gate keeps a candidate.
        self.best = None        # the current agent's configuration
        self.answers = None     # its answers on the practice claims
        self.version = 0        # its version number: v0, v1, ...
        self.undone = []        # changes the gate rejected (the meta-agent must not repeat them)
        self.history = []       # one row per generation, for the summary at the end

    # ------------------------------------------------------------------
    # The whole run
    # ------------------------------------------------------------------
    def run(self, start, generations):
        self.introduce(start)
        self.test_start(start)

        for g in range(1, generations + 1):
            if self.all_correct():
                break
            self.console.step()
            self.say(f"{B}━━ Generation {g} ━━{X}   current agent: v{self.version}, "
                     f"score {self.current_score()}/{len(self.practice)}\n")

            self.show_mistakes()                          # step 1
            try:
                proposal = self.diagnose()                # step 2
            except ReplayMissing:
                self.say(f"{Y}The recording ends here: this path was never run in class. "
                         f"Use --fresh with GEMINI_API_KEY to continue it live.{X}")
                break
            except Exception as e:
                self.say(f"{Y}The meta-model gave an invalid proposal ({e}). Skip.{X}")
                continue
            self.show_change(proposal)                    # step 3
            self.console.step()
            self.say(f"{B}━━ Generation {g} ━━{X}   candidate v{self.version + 1}: "
                     f"{proposal.part} changed\n")
            new_answers = self.test_candidate(proposal)   # step 4
            self.decide(proposal, new_answers)            # step 5
            self.llm.save()

        self.final_check(start)
        self.summary()
        self.llm.save()

    # ------------------------------------------------------------------
    # Before the first generation
    # ------------------------------------------------------------------
    def introduce(self, start):
        """Show the policy, the starting agent, and the text the model receives."""
        self.say(f"{B}A phone-insurance agent that improves itself{X}\n")
        self.say(f"{B}The company policy{X} (the agent does not know it yet)")
        for rule in self.policy.RULES:
            self.say(f"  {rule}", 0.3)
        self.say(f"\n{B}The starting agent v0{X} (agents/v0.json)")
        self.console.show_agent(start)
        self.say(f"\n{B}What the model receives{X} for claim C1 (built by the harness)")
        for line in self.harness.build_request(start, self.practice[0]).splitlines():
            self.say(f"  {D}│{X} {line}")
        self.console.step()

    def test_start(self, start):
        """Test v0 on the practice claims."""
        n = len(self.practice)
        self.say(f"{B}Test v0 on the {n} practice claims{X}\n")
        self.best = start
        self.answers = Agent(start, self.harness, self.llm).run(self.practice)
        self.console.table(self.practice, [("v0", self.answers)])
        self.say(f"\n{D}v0 gets {self.current_score()}/{n} right by guessing: "
                 f"it knows no rules and sees only the description.{X}")
        self.history.append(("v0", "start", "-", self.current_score(), "-"))
        self.llm.save()

    # ------------------------------------------------------------------
    # The five steps of one generation
    # ------------------------------------------------------------------
    def show_mistakes(self):
        """Step 1: list the claims the current agent answers wrongly."""
        self.say(f"{B}1 Mistakes{X}")
        for c, a in zip(self.practice, self.answers):
            if a != c.truth:
                reason = "" if c.why == "ok" else f" ({c.why})"
                self.say(f"  {c.id} {c.name:8} said {a:8} correct answer {c.truth}{reason}", 0.2)

    def diagnose(self):
        """Step 2: the meta-agent finds the cause and proposes one change."""
        proposal = self.meta_agent.propose(self.best, self.practice, self.answers, self.undone)
        self.say(f"\n{B}2 Diagnosis{X} (meta-model)")
        self.say(textwrap.fill(proposal.diagnosis, 88, initial_indent="  ", subsequent_indent="  "), 1)
        self.say(f"  kind of problem: {Y}{proposal.kind.upper()}{X}  ->  "
                 f"part to change: {C}{proposal.part.upper()}{X}", 1)
        return proposal

    def show_change(self, proposal):
        """Step 3: show what the candidate changes."""
        self.say(f"\n{B}3 Change one part{X} -> candidate v{self.version + 1}")
        self.console.show_change(proposal.part, self.best, proposal.candidate)
        self.llm.save()

    def test_candidate(self, proposal):
        """Step 4: test the candidate on the SAME practice claims, and compare."""
        self.say(f"{B}4 Test the candidate on the same {len(self.practice)} claims{X}\n")
        new_answers = Agent(proposal.candidate, self.harness, self.llm).run(self.practice)
        self.console.table(self.practice, [(f"v{self.version}", self.answers),
                                           (f"v{self.version + 1}", new_answers)])
        return new_answers

    def decide(self, proposal, new_answers):
        """Step 5: the gate keeps the candidate or undoes the change."""
        self.say(f"\n{B}5 Decide{X}")
        decision = self.gate.decide(self.answers, new_answers, self.practice)
        new_score = score(new_answers, self.practice)

        if decision.keep:
            self.version += 1
            proposal.candidate.save(self.agents_dir / f"v{self.version}.json")
            self.best, self.answers = proposal.candidate, new_answers
            self.say(f"  {G}KEEP v{self.version}{X}: {decision.reason}. "
                     f"Saved agents/v{self.version}.json", 1)
            self.history.append((f"v{self.version}", proposal.part, proposal.kind, new_score, "KEEP"))
        else:
            self.say(f"  {R}UNDO{X}: {decision.reason}. We stay with v{self.version}.", 1)
            fixed = fixed_ids(self.practice, self.answers, new_answers)
            broke = fixed_ids(self.practice, new_answers, self.answers)
            changed_to = json.dumps(proposal.candidate.part(proposal.part))
            self.undone.append(f"{proposal.part} set to {changed_to}: fixed {fixed}, broke {broke}")
            self.history.append(("-", proposal.part, proposal.kind, new_score, "UNDO"))

        if self.all_correct():
            self.say(f"  All {len(self.practice)} practice claims are right, so the loop stops.")

    # ------------------------------------------------------------------
    # After the last generation
    # ------------------------------------------------------------------
    def final_check(self, start):
        """Test the first and the final agent on the exam claims, never used above."""
        self.console.step()
        self.say(f"{B}Final check: 5 exam claims the loop never saw{X}\n")
        exam = self.claims.exam
        first = Agent(start, self.harness, self.llm).run(exam)
        final = Agent(self.best, self.harness, self.llm).run(exam)
        self.console.table(exam, [("v0", first), (f"v{self.version}", final)])

    def summary(self):
        """One row per generation: which part changed, the score, and the decision."""
        n = len(self.practice)
        self.say(f"\n{B}What changed{X}")
        self.say(f"{D}  {'version':9}{'part':9}{'problem':13}{'practice':>8}  decision{X}")
        for v, part, kind, s, d in self.history:
            colour = G if d == "KEEP" else R if d == "UNDO" else ""
            self.say(f"  {v:9}{part:9}{kind:13}{f'{s}/{n}':>8}  {colour}{d}{X}", 0.3)
        self.say(f"\n{D}Restore the defaults any time: python3 main.py --reset{X}")

    # ------------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------------
    def current_score(self):
        return score(self.answers, self.practice)

    def all_correct(self):
        return self.current_score() == len(self.practice)
