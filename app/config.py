import os
import decimal
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://user:pass@localhost:5432/ai_chat_db"
    )
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")

    # Подставь актуальные цены с сайта OpenAI
    INPUT_PRICE_PER_1K = decimal.Decimal("0.0005")
    OUTPUT_PRICE_PER_1K = decimal.Decimal("0.0015")

    MODEL_NAME = "gpt-4.1-mini"

settings = Settings()

if not settings.OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")
print("DATABASE_URL repr:", repr(settings.DATABASE_URL))
