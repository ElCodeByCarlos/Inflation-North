"""Start the API in development mode: py run.py"""
import os

import uvicorn

# OneDrive-synced folders don't reliably emit native file-change events, so the
# reloader can miss new files (new routes then 404 until a manual restart).
# Polling is slightly heavier but always picks up changes.
os.environ.setdefault("WATCHFILES_FORCE_POLLING", "true")

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
