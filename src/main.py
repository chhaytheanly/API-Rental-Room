from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from src.app.config import init_scheduler, shutdown_scheduler
from src.app.routes import (
    billing_router,
    invoice_router,
    loggin_router,
    room_router,
    tenant_router,
    user_router,
)

app = FastAPI(title="Room Management API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = APIRouter(prefix="/api/v1")
app.include_router(prefix=router.prefix, router=loggin_router)
app.include_router(prefix=router.prefix, router=user_router)
app.include_router(prefix=router.prefix, router=room_router)
app.include_router(prefix=router.prefix, router=billing_router)
app.include_router(prefix=router.prefix, router=tenant_router)
app.include_router(prefix=router.prefix, router=invoice_router)

# Serve static files from the "uploads" directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/public", StaticFiles(directory="src/public"), name="public" )

@app.get("/", response_class=HTMLResponse)
def home():
    html_path = "src/index.html"
    with open(html_path, "r", encoding="utf-8", errors="replace") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)

# Start Scheduler Every months via Cron Job
@app.on_event("startup")
def on_startup():
    init_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()
