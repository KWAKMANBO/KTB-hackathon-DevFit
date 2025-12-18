from fastapi import FastAPI
from contextlib import asynccontextmanager

from db.mongodb import connect_db, close_db
from db.repositories import candidate_repository

from api.routes.upload_router import router as upload_router
from api.routes.analyze_router import router as analyze_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    await candidate_repository.create_indexes()
    yield
    await close_db()


app = FastAPI(
    title="CultureFit AI",
    description="개발자 취준생을 위한 AI 기반 컬쳐핏 분석 서비스",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(upload_router)
app.include_router(analyze_router)

@app.get("/")
def read_root():
    return {"message": "CultureFit AI API"}

