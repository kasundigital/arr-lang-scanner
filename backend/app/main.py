from pathlib import Path

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .routes import search, languages, auth
from .utils.auth import require_auth

app = FastAPI(
    title="Sonarr/Radarr Audio Language Scanner",
    version="1.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")

app.include_router(
    search.router,
    prefix="/api",
    dependencies=[Depends(require_auth)],
)
app.include_router(
    languages.router,
    prefix="/api",
    dependencies=[Depends(require_auth)],
)


@app.get("/health")
def health():
    return {"status": "ok"}


BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR), html=False),
    name="static",
)


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")
