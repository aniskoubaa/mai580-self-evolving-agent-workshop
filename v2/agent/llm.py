"""LLM — calls Gemini, or replays the answers recorded in class (no key, no internet).

Responsibility: send one text to a model and return its reply.

YOU DO NOT NEED TO READ THIS FILE FOR THE TASKS.
It is plumbing: hashing, HTTP and retries. Use it like this:  llm.ask(model, text)
"""
import hashlib
import json
import os
import time
import urllib.request

class ReplayMissing(RuntimeError):
    """The recording has no answer for this request: it was never run in class."""


URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"


class LLM:
    def __init__(self, recorded, cache, fresh=False):
        self.cache_path = cache
        self.fresh = fresh          # True: call Gemini. False: replay only.
        source = cache if cache.exists() else recorded
        self.answers = json.loads(source.read_text()) if source.exists() else {}

    def ask(self, model, text, temperature=0.0):
        key = hashlib.sha256(f"{model}|{temperature}|{text}".encode()).hexdigest()
        if key in self.answers and not self.fresh:
            return self.answers[key]
        if not self.fresh:
            raise ReplayMissing(
                "No recorded answer matches this request. Replay supports the original "
                "demo only. Restore the original configuration, or use --fresh with "
                "GEMINI_API_KEY to evaluate changes with live model calls.")
        self.answers[key] = self._call_gemini(model, text, temperature)
        return self.answers[key]

    def _call_gemini(self, model, text, temperature):
        url = URL.format(model=model, key=os.environ["GEMINI_API_KEY"])
        body = json.dumps({"contents": [{"parts": [{"text": text}]}],
                           "generationConfig": {"temperature": temperature}}).encode()
        for attempt in range(4):
            try:
                request = urllib.request.Request(url, body, {"Content-Type": "application/json"})
                reply = json.load(urllib.request.urlopen(request, timeout=120))
                return "".join(p.get("text", "") for p in reply["candidates"][0]["content"]["parts"])
            except Exception:       # rate limit or network: wait, then retry
                if attempt == 3:
                    raise
                time.sleep(2 ** attempt * 3)

    def save(self):
        self.cache_path.parent.mkdir(exist_ok=True)
        self.cache_path.write_text(json.dumps(self.answers))
