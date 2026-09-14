from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from . import storage
from .routes import auth, languages, search, settings
from .utils.auth import require_auth

storage.init_db()

app = FastAPI(
    title="Sonarr/Radarr Audio Language Scanner",
    version="1.4.0",
    docs_url="/api/docs",
    redoc_url=None,
)

app.include_router(auth.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(search.router, prefix="/api", dependencies=[Depends(require_auth)])
app.include_router(languages.router, prefix="/api", dependencies=[Depends(require_auth)])


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "service": "arr-lang-scanner", "version": "1.4.0"}


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR), html=False), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")
