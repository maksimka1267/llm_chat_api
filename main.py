from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from app.database import init_db
from app.routers import sessions as sessions_router
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent

print("DATABASE_URL repr:", repr(settings.DATABASE_URL))

# створюємо таблиці, якщо їх ще немає
init_db()

app = FastAPI(title="API для AI-чату з підрахунком вартості")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # на проді краще обмежити
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_router.router)


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "pages" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
