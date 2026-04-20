"""
CoolNest — start script.
Starts the FastAPI + uvicorn server on port 7778.

Access via JupyterLab proxy:
  https://<notebook-url>/proxy/7778/

Usage:
  python serve.py          # start server (assumes frontend already built)
  python serve.py --build  # build frontend first, then start server
  python serve.py --setup  # create BQ tables + seed data (run once)
"""
import os
import sys
import subprocess

PORT = 7778
DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND = os.path.join(DIR, "backend")
FRONTEND = os.path.join(DIR, "frontend")

NOTEBOOK_URL_HINT = "https://c512bc0eae6aef0-dot-asia-southeast1.notebooks.googleusercontent.com"


def print_banner():
    print(f"""
{'─'*60}
  🏠  CoolNest Voice Agent
{'─'*60}
  Access your app:
  → {NOTEBOOK_URL_HINT}/proxy/{PORT}/

  Replace the path in your JupyterLab URL:
    FROM: https://...notebooks.google.com/lab/...
    TO:   https://...notebooks.google.com/proxy/{PORT}/

  Ctrl+C to stop.
{'─'*60}
""")


def build_frontend():
    print("📦 Building React frontend...")
    dist = os.path.join(FRONTEND, "dist")
    if not os.path.isdir(os.path.join(FRONTEND, "node_modules")):
        print("  Installing npm packages...")
        subprocess.run(["npm", "install"], cwd=FRONTEND, check=True)
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND, check=True)
    print(f"  ✓ Frontend built → {dist}")


def setup_bq():
    print("🗄️  Setting up BigQuery tables...")
    subprocess.run([sys.executable, "bq_setup.py"], cwd=BACKEND, check=True)


def start_server():
    import uvicorn
    sys.path.insert(0, BACKEND)
    os.chdir(BACKEND)
    print_banner()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=PORT,
        reload=False,
        log_level="warning",
    )


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--setup" in args:
        sys.path.insert(0, BACKEND)
        setup_bq()
        print("✅ BigQuery setup complete.")
        sys.exit(0)

    if "--build" in args:
        build_frontend()

    # Check frontend is built
    if not os.path.isfile(os.path.join(FRONTEND, "dist", "index.html")):
        print("⚠️  Frontend not built. Running build now...")
        build_frontend()

    start_server()
