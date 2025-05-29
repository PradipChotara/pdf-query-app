from fastapi import FastAPI
from app.api import routes

app = FastAPI()

# Include API routes
app.include_router(routes.router)