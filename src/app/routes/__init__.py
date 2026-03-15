from src.app.routes.billing import router as billing_router
from src.app.routes.invoice import invoice_router
from src.app.routes.login import loggin_router
from src.app.routes.room import room_router
from src.app.routes.tenant import tenant_router
from src.app.routes.user import user_router

all_routers = [
    loggin_router,
    user_router,
    room_router,
    billing_router,
    tenant_router,
    invoice_router,
]

__all__ = [
    "all_routers",
    "billing_router",
    "invoice_router",
    "loggin_router",
    "room_router",
    "tenant_router",
    "user_router",
]
