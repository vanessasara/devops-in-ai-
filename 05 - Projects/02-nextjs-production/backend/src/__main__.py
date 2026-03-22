"""Entry point for `python -m src` (same server as `python main.py`)."""

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)