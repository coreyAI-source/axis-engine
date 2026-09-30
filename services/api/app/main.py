from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import async_engine
from .config import settings
from .models.base import Base
from .routers import (
    auth,
    organisations,
    sites,
    users,
    roles,
    processes,
    standards,
    clauses,
    process_clause_maps,
    monitoring_tasks,
    monitoring_runs,
    audits,
    audit_prompts,
    evidence,
    findings,
    actions,
    reports,
    dashboard,
    hospitality,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tables are managed by Alembic in production.
    # In development/test, create_all is convenient.
    if settings.auto_create_tables:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="AXIS Integrated Compliance Engine",
    description="ISO 9001 / ISO 14001 / ISO 45001 compliance management platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router)
app.include_router(organisations.router)
app.include_router(sites.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(processes.router)
app.include_router(standards.router)
app.include_router(clauses.router)
app.include_router(process_clause_maps.router)
app.include_router(monitoring_tasks.router)
app.include_router(monitoring_runs.router)
app.include_router(audits.router)
app.include_router(audit_prompts.router)
app.include_router(evidence.router)
app.include_router(findings.router)
app.include_router(actions.router)
app.include_router(reports.router)
app.include_router(dashboard.router)
app.include_router(hospitality.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "axis-api"}
