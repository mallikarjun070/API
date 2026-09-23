import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

from database.db import init_db
from routes import auth_router, users_router, resume_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    print("🚀 Initializing database tables...")
    init_db()
    print("✅ Database tables initialized successfully.")
    yield
    # Shutdown logic if any
    print("🛑 Shutting down AI Resume Builder backend.")


app = FastAPI(
    title=os.getenv("APP_NAME", "AI Resume Builder API"),
    version="1.0.0",
    description="Production-ready REST API for AI Resume Builder with JWT Auth, ATS scoring, AI bullet enhancements, and PDF generation.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware Configuration
cors_origins_str = os.getenv("CORS_ORIGINS", "*")
origins = ["*"] if cors_origins_str == "*" else [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(resume_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "status": "online",
        "service": "AI Resume Builder Backend API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "database": "connected"
    }


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    reload = os.getenv("DEBUG", "True").lower() in ("true", "1")
    
    print(f"Starting server on http://{host}:{port} (docs: http://{host}:{port}/docs)")
    uvicorn.run("app:app", host=host, port=port, reload=reload)
