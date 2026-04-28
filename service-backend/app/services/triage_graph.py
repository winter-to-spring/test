"""Placeholder — Phase 2 fills in the LangGraph triage pipeline.

Required: classify(message: str) -> Literal["urgent", "normal", "spam"]
          summarize(message: str) -> str  (≤200 chars)
          run_pipeline(raw_text: str) -> dict[str, str]
            returns {"priority": ..., "summary": ...}
"""

def run_pipeline(raw_text: str) -> dict:
    raise NotImplementedError("Phase 2 mission fills this in")
