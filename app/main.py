from fastapi import FastAPI

from app.routers import jwt_auth, albums, medias

app = FastAPI(debug=True)
app.include_router(jwt_auth.router)
app.include_router(albums.router)
app.include_router(medias.router)


@app.get("/")
async def root():
    return {"message": "Welcome to RieGalgo API"}
