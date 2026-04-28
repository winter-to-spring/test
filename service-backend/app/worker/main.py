"""Placeholder — Phase 2 fills in the worker loop.

Required: poll raw_events WHERE processed=False every 1s,
push each through services.triage_graph.run_pipeline,
write to notifications, mark raw_events.processed=True.
Run as `python -m app.worker.main`.
"""

if __name__ == "__main__":
    raise NotImplementedError("Phase 2 mission fills this in")
