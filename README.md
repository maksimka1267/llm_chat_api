# LLM Chat API

Невеликий сервіс на **FastAPI**, який:
- створює сесії чату;
- відправляє повідомлення до **OpenAI API**;
- зберігає всю історію діалогу в PostgreSQL;
- рахує токени та **вартість** кожної відповіді й всієї сесії.

Є проста веб-сторінка на `/`, яка дозволяє протестувати API без додаткового фронтенду.

---

## Технології

- **Python 3.12+**
- **FastAPI** + Uvicorn
- **SQLAlchemy** + PostgreSQL
- **psycopg** (PostgreSQL драйвер)
- **OpenAI API**
- Чиста HTML/JS сторінка (`pages/index.html`)

---

## Структура проєкту

```text
llm_chat_api/
├─ app/
│  ├─ __init__.py
│  ├─ config.py          # налаштування: DATABASE_URL, OPENAI_API_KEY, модель, ціни
│  ├─ database.py        # engine, SessionLocal, Base, init_db()
│  ├─ models.py          # ChatSession, Message (SQLAlchemy-моделі)
│  ├─ schemas.py         # Pydantic-схеми запитів/відповідей
│  ├─ openai_client.py   # клієнт OpenAI + розрахунок вартості
│  └─ routers/
│     ├─ __init__.py
│     └─ sessions.py     # маршрути /sessions/…
├─ pages/
│  └─ index.html         # головна сторінка з UI для тесту
├─ main.py               # створення FastAPI-додатку, підключення роутерів, віддача index.html
├─ requirements.txt
└─ .env.example
````

---

## Налаштування

1. Створи базу даних у PostgreSQL, наприклад:

```sql
CREATE DATABASE ai_chat_db;
```

2. Заповни `.env` (можна взяти `.env.example` як шаблон):

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/ai_chat_db
OPENAI_API_KEY=sk-...
```

> **Увага:** для реальної роботи потрібен активний білінг / кредити в OpenAI.
> Без цього API буде повертати помилку `insufficient_quota (429)`.

3. Встанови залежності:

```bash
pip install -r requirements.txt
```

---

## Запуск локально

```bash
python main.py
```

або

```bash
uvicorn main:app --reload
```

Після цього:

* головна сторінка: `http://127.0.0.1:8000/`
* документація (Swagger): `http://127.0.0.1:8000/docs`

---

## Головна сторінка (`/`)

На сторінці `pages/index.html` доступно:

1. **Створення сесії** (може викликатися автоматично або вручну).
2. **Відправка повідомлення** до моделі.
3. **Перегляд історії сесії** (усі повідомлення + сума токенів і загальна вартість).

Весь текст інтерфейсу — українською.

---

## Ендпоінти API

### 1. Створити нову сесію

**POST** `/sessions`

#### Відповідь 200

```json
{
  "session_id": "2b5b5e7a-6d6c-4ec6-b6f0-7c7f9c0f4c41",
  "created_at": "2025-11-18T15:23:01.123456"
}
```

---

### 2. Надіслати повідомлення в сесію

**POST** `/sessions/{session_id}/messages`

#### Тіло запиту

```json
{
  "message": "Привіт! Поясни, як працює логістична регресія."
}
```

#### Відповідь 200 (приклад)

```json
{
  "reply": "Тут буде текст відповіді моделі українською...",
  "prompt_tokens": 50,
  "completion_tokens": 120,
  "total_tokens": 170,
  "message_cost_usd": "0.000255",
  "session_total_cost_usd": "0.000510"
}
```

У відповідь повертається:

* відповідь моделі;
* скільки токенів було використано;
* вартість саме цього повідомлення;
* накопичена вартість всієї сесії.

---

### 3. Отримати повну історію сесії

**GET** `/sessions/{session_id}`

#### Відповідь 200 (приклад)

```json
{
  "session_id": "2b5b5e7a-6d6c-4ec6-b6f0-7c7f9c0f4c41",
  "created_at": "2025-11-18T15:23:01.123456",
  "total_prompt_tokens": 100,
  "total_completion_tokens": 240,
  "total_cost_usd": "0.000765",
  "messages": [
    {
      "role": "user",
      "content": "Привіт!",
      "created_at": "2025-11-18T15:23:02.000000",
      "prompt_tokens": null,
      "completion_tokens": null,
      "cost_usd": null
    },
    {
      "role": "assistant",
      "content": "Привіт! Чим я можу допомогти?",
      "created_at": "2025-11-18T15:23:03.000000",
      "prompt_tokens": 20,
      "completion_tokens": 40,
      "cost_usd": "0.000120"
    }
  ]
}
```

---

### 4. Видалити сесію

**DELETE** `/sessions/{session_id}`

#### Відповідь 200

```json
{
  "status": "ok",
  "message": "Сесію видалено"
}
```

---

## Примітки

* Усі тексти, що бачить користувач (UI, повідомлення про помилки) — **українською**.
* Логіка розрахунку вартості знаходиться в `app/openai_client.py`, ціни задаються в `app/config.py`:

  * `INPUT_PRICE_PER_1K`
  * `OUTPUT_PRICE_PER_1K`
* Моделі чату та зберігання історії сесій реалізовано через `ChatSession` та `Message` в `app/models.py`.

---

```
::contentReference[oaicite:0]{index=0}
```
