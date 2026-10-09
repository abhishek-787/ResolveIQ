from datetime import (
    datetime,
    timezone,
)

from sqlalchemy.orm import Session

from app.models import (
    Conversation,
)

from app.models.enums import (
    MessageSender,
)

from app.repositories.conversation import (
    create_conversation,
    create_message,
    get_conversation,
    list_recent_messages,
)

def start_conversation(
    db: Session,
) -> Conversation:

    conversation = (
        create_conversation(
            db=db
        )
    )

    db.commit()

    db.refresh(
        conversation
    )

    return conversation

def require_conversation(
    db: Session,
    conversation_id: int,
) -> Conversation:

    conversation = (
        get_conversation(
            db=db,
            conversation_id=conversation_id,
        )
    )

    if conversation is None:
        raise ValueError(
            "Conversation not found."
        )

    return conversation

def load_conversation_history(
    db: Session,
    conversation_id: int,
    limit: int = 12,
) -> list[dict]:

    require_conversation(
        db=db,
        conversation_id=conversation_id
    )

    messages = (
        list_recent_messages(
            conversation_id=conversation_id,
            db=db,
            limit=limit,
        )
    )

    return [
        {
            "message_id":
                message.id,

            "sender":
                message.sender.value,

            "content":
                message.content,

            "created_at":
                (
                    message.created_at
                    .isoformat()
                    if message.created_at
                    else None
                ),
        }

        for message in messages
    ]

def save_conversation_turn(
    db: Session,
    conversation_id: int,
    customer_message: str,
    agent_message: str,
) -> None:

    conversation = (
        require_conversation(
            db=db,
            conversation_id=(
                conversation_id
            ),
        )
    )

    try:
        create_message(
            db=db,
            conversation_id=conversation_id,
            sender=(
                MessageSender.CUSTOMER
            ),
            content=(
                customer_message
            ),
        )

        create_message(
                    db=db,
                    conversation_id=conversation_id,
                    sender=(
                        MessageSender.AGENT
                    ),
                    content=(
                        agent_message
                    ),
                )

        conversation.updated_at=(
            datetime.now(
                timezone.utc
            )
        )

        db.commit()

    except Exception:

        db.rollback()

        raise

