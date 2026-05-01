"""FastAPI entrypoint with auth, profile, transactions wired in."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine, Base
from app.routers import atms, reports, users, recommendations, auth, profile, transactions
from app.seed_data import seed

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart ATM Platform — secure fintech-grade ATM locator with AI recommendations.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    seed()


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# Routers
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(transactions.router)
app.include_router(atms.router)
app.include_router(reports.router)
app.include_router(users.router)
app.include_router(recommendations.router)