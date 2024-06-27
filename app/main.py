from fastapi import FastAPI

from app.routers import jwt_auth

app = FastAPI(debug=True)
app.include_router(jwt_auth.router)


@app.get("/")
async def root():
    return {"message": "Welcome to RieGalgo API"}
