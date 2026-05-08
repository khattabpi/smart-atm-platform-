from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.errors import register_exception_handlers
from app.cache.redis_client import RedisClient
from app.events.broker import EventBroker
from app.ws.pubsub_bridge import bridge as ws_bridge

# Routers (new v1 paths)
from app.api.v1 import auth, atms, recommendations, reports, transactions, profile
from app.ws.routes import router as ws_router

# DB init (existing)
from app.database import engine, Base
from app import seed_data  # noqa: keep your existing seed logic

configure_logging(settings.ENV)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("app.starting", env=settings.ENV)

    # DB tables (keep existing dev behavior)
    Base.metadata.create_all(bind=engine)
    try:
        seed_data.seed()  # if your seed exposes this; otherwise leave the import side-effect
    except Exception as e:
        logger.warning("seed.failed_or_skipped", error=str(e))

    # Infra clients
    await RedisClient.init()
    await EventBroker.init()
    await ws_bridge.start()

    logger.info("app.ready")
    yield

    # --- Shutdown ---
    logger.info("app.shutting_down")
    await ws_bridge.stop()
    await EventBroker.close()
    await RedisClient.close()


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
register_exception_handlers(app)

# Routers (existing API contracts preserved)
app.include_router(auth.router)
app.include_router(atms.router)
app.include_router(recommendations.router)
app.include_router(reports.router)
app.include_router(transactions.router)
app.include_router(profile.router)

# WebSocket routes
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "redis": RedisClient.is_healthy(),
        "broker": EventBroker.is_healthy(),
    }