from fastapi.staticfiles import StaticFiles
from .app.config.session import get_db
from fastapi import APIRouter, Depends, FastAPI
from .app.routes.user import user_router
from .app.routes.login import loggin_router

app = FastAPI(title="User Management API", version="1.0.0")

app.include_router(loggin_router)

router = APIRouter(prefix="/api/v1")

app.include_router(prefix=router.prefix, router=user_router)

# Serve static files from the "uploads" directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get(router.prefix + "/")
def read_root(db=Depends(get_db)):
    return {"Hello": "World"}
