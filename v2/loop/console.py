"""Console — everything printed on screen. The loop decides; the console only shows.

YOU DO NOT NEED TO READ THIS FILE FOR THE TASKS.
It contains colour codes and column widths only.
"""
import time

from loop.evaluation import score

G, R, Y, C, B, D, X = "\033[32m", "\033[31m", "\033[33m", "\033[36m", "\033[1m", "\033[2m", "\033[0m"


class Console:
    def __init__(self, slow=False, step=False):
        self.slow = 1.0 if slow else 0.0   # --slow: pause after each line
        self.step_mode = step              # --step: wait for Enter between screens

    def say(self, text="", pause=0.0):
        print(text, flush=True)
        time.sleep(pause * self.slow)

    def step(self):
        if self.step_mode:
            input(f"\n{D}[Enter] next{X}")
            print("\033[H\033[2J\033[3J", end="", flush=True)   # clear the screen

    # ---- the claims table ----
    def _facts(self, c):
        report = c.police_report if c.cause == "theft" else "-"
        truth = c.truth + ("" if c.why == "ok" else f" ({c.why})")
        return f" {c.id:6}{c.name:8}{c.cause:8}{c.days_to_report():>8}  {report:8}{truth:19}"

    def _mark(self, answer, c):
        return f"{answer:8}{G + '✓' if answer == c.truth else R + '✗'}{X}"

    def table(self, claims, columns):
        """columns: list of (version name, answers). One row per claim."""
        self.say(f"{D} {'claim':6}{'who':8}{'cause':8}{'days':>8}  {'report':8}{'correct answer':19}"
                 + "".join(f"{name:11}" for name, _ in columns) + X)
        for i, c in enumerate(claims):
            row = self._facts(c) + "".join(f"{self._mark(ans[i], c)}  " for _, ans in columns)
            if len(columns) == 2 and columns[0][1][i] != columns[1][1][i]:
                row += f"{G}fixed{X}" if columns[1][1][i] == c.truth else f"{R}broken{X}"
            self.say(row, 0.25)
        self.say(f" {'score':{len(self._facts(claims[0])) - 1}}" + "".join(
            f"{B}{str(score(ans, claims)) + '/' + str(len(claims)):11}{X}" for _, ans in columns))

    # ---- the agent and its changes ----
    def show_agent(self, config):
        self.say(f"  {C}PROMPT {X}  " + f"\n  {' ' * 9}".join(config.prompt))
        self.say(f"  {C}HARNESS{X}  sends the model these claim fields: {', '.join(config.send_fields)}")
        self.say(f"  {C}TOOLS  {X}  {', '.join(config.tools) or 'none'}")

    def show_change(self, part, old, new):
        self.say(f"  {C}{part.upper()}{X}")
        if part == "prompt":
            for line in old.prompt:
                if line not in new.prompt:
                    self.say(f"  {R}- {line}{X}", 0.2)
            for line in new.prompt:
                self.say(f"  {G}+ {line}{X}" if line not in old.prompt else f"    {line}", 0.2)
        elif part == "harness":
            added = [f for f in new.send_fields if f not in old.send_fields]
            self.say(f"    sends: {', '.join(old.send_fields)}  {G}+ {', '.join(added)}{X}")
        else:
            self.say(f"    tools: {', '.join(old.tools) or 'none'}  ->  {G}{', '.join(new.tools)}{X}")
