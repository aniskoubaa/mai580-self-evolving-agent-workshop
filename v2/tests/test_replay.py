"""The recorded class run must replay unchanged: v0 6/10 -> v3 10/10, exam 3/5 -> 5/5."""
import io
import pathlib
import re
import tempfile
import unittest
from contextlib import redirect_stdout

from agent import AgentConfig, Harness, LLM
from claims import ClaimSet, Policy
from gate import ScoreGate
from loop.console import Console
from loop.evolution_loop import EvolutionLoop
from meta_agent import MetaAgent
from tools import ToolLibrary

DATA = pathlib.Path(__file__).parent.parent / "data"


class TestReplay(unittest.TestCase):
    def test_recorded_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = pathlib.Path(tmp)
            claims, policy, tools = ClaimSet.load(DATA / "claims.json"), Policy(), ToolLibrary()
            llm = LLM(recorded=DATA / "recorded_run.json", cache=tmp / "cache.json")
            harness = Harness(tools)
            loop = EvolutionLoop(claims, policy, harness, llm, MetaAgent(llm, harness, policy, tools),
                                 ScoreGate(), Console(), tmp)
            out = io.StringIO()
            with redirect_stdout(out):
                loop.run(start=AgentConfig.default(), generations=4)
            text = re.sub(r"\033\[[0-9;]*m", "", out.getvalue())   # drop the colours

        self.assertIn("v0 gets 6/10 right", text)
        self.assertIn("KEEP v3: 10/10 is better than 8/10", text)
        exam_scores = text.split("Final check")[1].split("What changed")[0]
        self.assertRegex(exam_scores, r"score\s+3/5\s+5/5")
