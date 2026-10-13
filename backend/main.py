"""
CRIMENET-X - Criminal Network Intelligence & Incident Analysis System
Main FastAPI application entry point.

ACADEMIC PROTOTYPE - All data is synthetic and for demonstration only.
No real personal data. No automated enforcement decisions.
Human review is always required.
"""
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.config import settings
from backend.database.database import init_db
from backend.database.seed import run_seed
from backend.websocket.manager import manager

# API routers
from backend.api.events import router as events_router
from backend.api.nodes import router as nodes_router
from backend.api.networks import router as networks_router
from backend.api.alerts import router as alerts_router
from backend.api.analytics import router as analytics_router
from backend.api.hotspots import router as hotspots_router
from backend.api.demo import router as demo_router
from backend.api.data import router as data_router

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("crimenet_x")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("Starting CRIMENET-X...")
    init_db()
    run_seed()
    logger.info("Database ready.")
    yield
    logger.info("CRIMENET-X shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
PREFIX = settings.API_PREFIX
app.include_router(events_router, prefix=PREFIX)
app.include_router(nodes_router, prefix=PREFIX)
app.include_router(networks_router, prefix=PREFIX)
app.include_router(alerts_router, prefix=PREFIX)
app.include_router(analytics_router, prefix=PREFIX)
app.include_router(hotspots_router, prefix=PREFIX)
app.include_router(demo_router, prefix=PREFIX)
app.include_router(data_router, prefix=PREFIX)


@app.get("/api/health")
def health_check():
    return {
        "status": "operational",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "online",
        "analytics": "ready",
        "websocket": "live",
    }


# WebSocket endpoint
@app.websocket("/ws/events")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        await manager.send_personal(
            {"type": "connected", "message": "CRIMENET-X WebSocket Live"},
            websocket,
        )
        while True:
            # Keep alive - receive ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await manager.send_personal({"type": "pong"}, websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Serve frontend static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
frontend_path = os.path.abspath(frontend_path)

if os.path.exists(frontend_path):
    # Mount assets directory
    assets_path = os.path.join(frontend_path, "assets")
    if os.path.exists(assets_path):
        app.mount("/assets", StaticFiles(directory=assets_path), name="assets")
    
    # Mount CSS
    css_path = os.path.join(frontend_path, "css")
    if os.path.exists(css_path):
        app.mount("/css", StaticFiles(directory=css_path), name="css")
    
    # Mount JS
    js_path = os.path.join(frontend_path, "js")
    if os.path.exists(js_path):
        app.mount("/js", StaticFiles(directory=js_path), name="js")
    
    # Mount pages
    pages_path = os.path.join(frontend_path, "pages")
    if os.path.exists(pages_path):
        app.mount("/pages", StaticFiles(directory=pages_path), name="pages")

    @app.get("/", response_class=FileResponse)
    @app.get("/index.html", response_class=FileResponse)
    def serve_index():
        index_path = os.path.join(frontend_path, "index.html")
        return FileResponse(index_path)

else:
    @app.get("/")
    def root():
        return {"message": "CRIMENET-X API", "docs": "/docs", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
