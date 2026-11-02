"""Minimal API entry point for ReliantOps."""

from fastapi import FastAPI

app = FastAPI(title="ReliantOps", version="0.1.0")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a lightweight health status."""
    return {"status": "ok"}
