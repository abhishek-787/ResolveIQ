from fastapi import (
    FastAPI,
)

from app.core.config import (
    settings,
)

from app.api.customers import (
    router as customers_router,
)
from app.api.orders import (
    router as orders_router,
)
from app.api.tickets import (
    router as tickets_router,
)

from app.api.admin_documents import (
    router as admin_documents_router,
)

from app.api.retrieval import (
    router as retrieval_router,
)

from app.api.support_agent import (
    router as support_agent_router,
)

from app.api.admin_approvals import (
    router as admin_approvals_router,
)

from app.api.support_vision import (
    router as support_vision_router,
)

from app.api.admin_observability import (
    router as admin_observability_router,
)
from fastapi.middleware.cors import (
    CORSMiddleware,
)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)

@app.get(
    "/health",
    tags=["System"],
)
def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }

app.include_router(
    customers_router
)

app.include_router(
    orders_router
)

app.include_router(
    tickets_router
)

app.include_router(
    admin_documents_router
)

app.include_router(
    retrieval_router
)

app.include_router(
    support_agent_router
)

app.include_router(
    support_vision_router
)

app.include_router(
    admin_approvals_router
)

app.include_router(
    admin_observability_router
)

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],

    allow_credentials=True,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
)