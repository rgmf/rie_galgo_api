from fastapi import FastAPI

from app.routers import jwt_auth
from app.database.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(debug=True)
app.include_router(jwt_auth.router)


@app.get("/")
async def root():
    return {"message": "Welcome to RieGalgo API"}
