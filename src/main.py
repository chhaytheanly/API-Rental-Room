from fastapi.staticfiles import StaticFiles
from .app.config.session import get_db
from fastapi import APIRouter, Depends, FastAPI
from .app.routes.user import user_router
from .app.routes.login import loggin_router
from .app.routes.room import room_router

app = FastAPI(title="Room Management API", version="1.0.0")

router = APIRouter(prefix="/api/v1")
app.include_router(prefix=router.prefix, router=loggin_router)
app.include_router(prefix=router.prefix, router=user_router)
app.include_router(prefix=router.prefix, router=room_router)

# Serve static files from the "uploads" directory
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get(router.prefix + "/")
def read_root(db=Depends(get_db)):
    return {"Hello": "World"}
