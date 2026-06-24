# Run with (from API/ dir): uvicorn main:app --reload
# Docs at:  http://127.0.0.1:8000/docs

from fastapi import FastAPI
from routers import all_routers

app = FastAPI(title="Elden Ring API")

for router in all_routers:
    app.include_router(router)
