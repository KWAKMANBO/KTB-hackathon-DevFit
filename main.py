from fastapi import FastAPI
from contextlib import asynccontextmanager
from db.mongodb import connect_db, close_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}
