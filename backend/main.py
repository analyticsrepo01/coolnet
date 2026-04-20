"""CoolNest FastAPI application — serves React frontend + WebSocket + REST API."""
import os
import sys

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from auth import authenticate, hash_token, verify_token
from config import USERS, PORT
from ws_handler import handle_websocket

app = FastAPI(title="CoolNest Voice Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (React build) ───────────────────────────────────────────────
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")

if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

# Serve avatar images from the public folder (not part of Vite build)
AVATARS_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "avatars")
if os.path.isdir(AVATARS_DIR):
    app.mount("/avatars", StaticFiles(directory=AVATARS_DIR), name="avatars")

AUDIO_PROC_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "audio-processors")
if os.path.isdir(AUDIO_PROC_DIR):
    app.mount("/audio-processors", StaticFiles(directory=AUDIO_PROC_DIR), name="audio-processors")

PRODUCTS_IMG_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "products")
if os.path.isdir(PRODUCTS_IMG_DIR):
    app.mount("/products", StaticFiles(directory=PRODUCTS_IMG_DIR), name="product-images")

PDFS_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "public", "pdfs")
if os.path.isdir(PDFS_DIR):
    app.mount("/pdfs", StaticFiles(directory=PDFS_DIR), name="pdfs")


# ── REST endpoints ───────────────────────────────────────────────────────────

@app.post("/api/login")
async def login(body: dict):
    user_id = body.get("user_id", "").strip().lower()
    password = body.get("password", "")
    user = authenticate(user_id, password)
    if not user:
        return JSONResponse({"error": "Invalid credentials"}, status_code=401)
    token = hash_token(user_id, password)
    return {"token": token, "user": user}


@app.get("/api/me")
async def get_me(user_id: str, token: str):
    user = verify_token(user_id, token)
    if not user:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return user


@app.get("/api/agents")
async def list_agents():
    from agents import AGENTS, agent_public_info
    return [agent_public_info(a) for a in AGENTS.values()]


@app.get("/api/products")
async def list_products(category: str = None):
    from products import PRODUCTS, get_category_products
    if category:
        return get_category_products(category)
    return list(PRODUCTS.values())


@app.get("/api/products/{sku}")
async def get_product(sku: str):
    from products import PRODUCTS
    product = PRODUCTS.get(sku.upper())
    if not product:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return product


@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "CoolNest"}


# ── WebSocket ────────────────────────────────────────────────────────────────

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await handle_websocket(websocket)


# ── Serve React app (catch-all must be last) ─────────────────────────────────

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index):
        return FileResponse(index)
    return JSONResponse({"error": "Frontend not built. Run: cd frontend && npm run build"}, status_code=503)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT, reload=False, log_level="info")
