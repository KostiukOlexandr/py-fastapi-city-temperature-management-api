from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.cities import router as cities_router
from app.routers.temperatures import router as temperatures_router


app = FastAPI(
    title="Weather API",
    description="API для міст та температур",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"name": "Team", "email": "support@example.com"},
    license_info={"name": "MIT"}
)


app.include_router(cities_router)
app.include_router(temperatures_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Weather API is running"}


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
