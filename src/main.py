from fastapi import APIRouter, Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from .app.config import get_db, init_scheduler, shutdown_scheduler
from .app.routes import (
    billing_router,
    invoice_router,
    loggin_router,
    room_router,
    tenant_router,
    user_router,
)
from .app.middleware.guard import PermissionGuard

app = FastAPI(title="Room Management API", version="1.0.0")

public_routes = [loggin_router]


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

permission = PermissionGuard.admin_only
print("Admin-only routes will be protected with PermissionGuard")

# Protect the routes that require admin access
for router in [user_router, room_router, billing_router, tenant_router]:
    for route in router.routes:
        if route not in [r for r in public_routes]:
            route.dependencies.append(Depends(permission))
        else:
            print(f"Route {route} is public and will not be protected with PermissionGuard")

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

@app.on_event("startup")
def on_startup():
    init_scheduler()


@app.on_event("shutdown")
def on_shutdown():
    shutdown_scheduler()

@app.get(router.prefix + "/")
def read_root(db=Depends(get_db)):
    return {"Hello": "World"}
