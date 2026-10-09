from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Conversation,
    Message,
)

from app.models.enums import (
    MessageSender,
)


def create_conversation(
    db: Session,
    customer_id: int | None = None,
    ticket_id: int | None = None,
) -> Conversation:

    conversation = Conversation(
        customer_id=customer_id,
        ticket_id=ticket_id,
    )

    db.add(
        conversation
    )

    db.flush()

    return conversation

def get_conversation(
    db: Session,
    conversation_id: int,
) -> Conversation | None:

    return db.get(
        Conversation,
        conversation_id,
    )

def create_message(
    db: Session,
    conversation_id: int,
    sender: MessageSender,
    content: str,
) -> Message:

    message = Message(
        conversation_id=conversation_id,
        sender=sender,
        content=content,
    )

    db.add(message)

    db.flush()

    return message

def list_recent_messages(
    db: Session,
    conversation_id: int,
    limit: int = 12,
) -> list[Message]:

    statement = (
        select(Message).where(Message.conversation_id == conversation_id).order_by(
            Message.created_at.desc(),Message.id.desc(),
        ).limit(limit)
    )

    messages = list(
        db.scalars(
            statement
        ).all()
    )

    messages.reverse()

    return messages