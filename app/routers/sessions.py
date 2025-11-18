from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from .. import models
from .. import schemas
from ..openai_client import client, calc_message_cost
from ..config import settings

router = APIRouter(prefix="/sessions", tags=["Сесії"])


@router.post("", response_model=schemas.StartSessionResponse)
def create_session(db: Session = Depends(get_db)):
    session = models.ChatSession()
    db.add(session)
    db.commit()
    db.refresh(session)
    return schemas.StartSessionResponse(
        session_id=session.id,
        created_at=session.created_at,
    )


@router.post("/{session_id}/messages", response_model=schemas.SendMessageResponse)
def send_message(
    session_id: str,
    body: schemas.SendMessageRequest,
    db: Session = Depends(get_db),
):
    session = db.query(models.ChatSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")

    history = (
        db.query(models.Message)
        .filter_by(session_id=session_id)
        .order_by(models.Message.created_at)
        .all()
    )

    messages_payload = [
        {"role": m.role, "content": m.content} for m in history
    ]
    messages_payload.append({"role": "user", "content": body.message})

    # зберігаємо повідомлення користувача
    user_msg = models.Message(
        session_id=session_id,
        role="user",
        content=body.message,
    )
    db.add(user_msg)
    db.commit()

    try:
        response = client.chat.completions.create(
            model=settings.MODEL_NAME,
            messages=messages_payload,
        )
    except Exception as e:
        text = str(e)
        if "insufficient_quota" in text:
            raise HTTPException(
                status_code=503,
                detail="OpenAI: перевищено квоту API. Поповніть баланс у кабінеті OpenAI."
            )
        raise HTTPException(
            status_code=500,
            detail="Внутрішня помилка при зверненні до OpenAI."
        )
    answer = response.choices[0].message.content
    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    msg_cost = calc_message_cost(prompt_tokens, completion_tokens)

    assistant_msg = models.Message(
        session_id=session_id,
        role="assistant",
        content=answer,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        cost_usd=msg_cost,
    )
    db.add(assistant_msg)

    session.total_prompt_tokens += prompt_tokens
    session.total_completion_tokens += completion_tokens
    session.total_cost_usd = session.total_cost_usd + msg_cost

    db.commit()
    db.refresh(session)

    return schemas.SendMessageResponse(
        reply=answer,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        message_cost_usd=msg_cost,
        session_total_cost_usd=session.total_cost_usd,
    )


@router.get("/{session_id}", response_model=schemas.SessionHistoryResponse)
def get_history(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")

    messages = (
        db.query(models.Message)
        .filter_by(session_id=session_id)
        .order_by(models.Message.created_at)
        .all()
    )

    return schemas.SessionHistoryResponse(
        session_id=session.id,
        created_at=session.created_at,
        total_prompt_tokens=session.total_prompt_tokens,
        total_completion_tokens=session.total_completion_tokens,
        total_cost_usd=session.total_cost_usd,
        messages=[schemas.MessageDTO.model_validate(m) for m in messages],
    )


@router.delete("/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    session = db.query(models.ChatSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Сесію не знайдено")
    db.delete(session)
    db.commit()
    return {"status": "ok", "message": "Сесію видалено"}
