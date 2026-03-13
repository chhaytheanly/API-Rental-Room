from .billing import router as billing_router
from .invoice import invoice_router
from .login import loggin_router
from .room import room_router
from .tenant import tenant_router
from .user import user_router

all_routers = [
    loggin_router,
    user_router,
    room_router,
    billing_router,
    tenant_router,
    invoice_router,
]
