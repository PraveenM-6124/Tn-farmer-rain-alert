"""Convenience launcher for Tamil Nadu Farmer Rain Alert application."""

import webbrowser

import uvicorn

if __name__ == "__main__":
    url = "http://tnfarmerweathernoti.com:8000"
    print("\n" + "=" * 65)
    print("  🌾 TAMIL NADU FARMER RAIN ALERT & MARKETPLACE")
    print("=" * 65)
    print(f"\n  Serving website at : {url}")
    print("  Local loopback URL : http://localhost:8000")
    print("\n  Opening browser...")
    print("=" * 65 + "\n")

    try:
        webbrowser.open(url)
    except Exception:
        pass

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
