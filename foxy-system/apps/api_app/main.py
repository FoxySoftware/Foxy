from fastapi import FastAPI

from api_app.routers import collector, health, projects


app = FastAPI(
    title="Foxy API",
    version="0.1.0",
    description="HTTP API for Foxy collector and processor workflows.",
)

app.include_router(health.router)
app.include_router(projects.router)
app.include_router(collector.router)
