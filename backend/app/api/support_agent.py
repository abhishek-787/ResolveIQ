from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
)

from app.services.support_image_storage import (
    save_support_image,
)

from app.services.vision_analysis import (
    analyze_support_image,
)

from sqlalchemy.orm import Session

from app.db.session import (
    get_db,
)

from app.services.conversation_memory import (
    load_conversation_history,
    require_conversation,
    save_conversation_turn,
    start_conversation,
)

from app.agent.graph import (
    support_graph,
)

from app.schemas.support_agent import (
    SupportRequest,
    SupportResponse,
    SupportSource,
)

from app.services.customer_history import (
    build_customer_history_context,
)

from app.services.observability import (
    invoke_support_graph_observed,
)
from app.agent.router import (
    route_support_request,
)


router = APIRouter(
    prefix="/support",
    tags=["Support Agent"],
)


@router.get(
    "/route",
)
def route_support_query(
    query: str = Query(
        ...,
        min_length=2,
    ),
):

    result = route_support_request(
        {
            "user_query": query,
            "conversation_id": None,
            "conversation_history": [],
            "memory_summary": (
                "No previous conversation "
                "history is available."
            ),
            "memory_identifiers": {},
            "vision_context": {},
        }
    )

    return {
        "query": query,

        "route":
            result.get(
                "route"
            ),

        "route_reason":
            result.get(
                "route_reason"
            ),

        "needs_business_data":
            result.get(
                "needs_business_data"
            ),

        "needs_knowledge":
            result.get(
                "needs_knowledge"
            ),

        "customer_code":
            result.get(
                "customer_code"
            ),

        "order_number":
            result.get(
                "order_number"
            ),

        "ticket_number":
            result.get(
                "ticket_number"
            ),
    }

@router.post(
    "/ask",
    response_model=SupportResponse,
)
def ask_support_agent(
    request: SupportRequest,
    db: Session = Depends(get_db),
):

    if request.conversation_id is None:

        conversation = (
            start_conversation(
                db=db
            )
        )

    else:

        try:

            conversation = (
                require_conversation(
                    db=db,
                    conversation_id=(
                        request.conversation_id
                    ),
                )
            )

        except ValueError:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Conversation not found."
                ),
            )

    conversation_id = (
        conversation.id
    )

    conversation_history = (
        load_conversation_history(
            db=db,
            conversation_id=(
                conversation_id
            ),
            limit=12,
        )
    )

    result, _ = (
        invoke_support_graph_observed(
            input_state={
                "user_query":
                    request.query,

                "conversation_id":
                    conversation_id,

                "conversation_history":
                    conversation_history,

                "vision_context": {},
            },

            run_type="support",
        )
    )

    final_answer = (
        result.get(
            "final_answer"
        )
        or (
            "I couldn't generate "
            "a response."
        )
    )

    save_conversation_turn(
        db=db,

        conversation_id=(
            conversation_id
        ),

        customer_message=(
            request.query
        ),

        agent_message=(
            final_answer
        ),
    )

    used_ids = set(
        result.get(
            "citations_used",
            [],
        )
    )

    knowledge_context = (
        result.get(
            "knowledge_context"
        )
        or {}
    )

    knowledge_data = (
        knowledge_context.get(
            "data"
        )
        or {}
    )

    all_citations = (
        knowledge_data.get(
            "citations"
        )
        or []
    )

    sources = []

    for citation in all_citations:

        if (
            citation.get(
                "citation_id"
            )
            not in used_ids
        ):
            continue

        sources.append(
            SupportSource(
                citation_id=(
                    citation[
                        "citation_id"
                    ]
                ),

                document_code=(
                    citation[
                        "document_code"
                    ]
                ),

                document_type=(
                    citation[
                        "document_type"
                    ]
                ),

                version_label=(
                    citation.get(
                        "version_label"
                    )
                ),

                section_title=(
                    citation[
                        "section_title"
                    ]
                ),

                source_filename=(
                    citation[
                        "source_filename"
                    ]
                ),
            )
        )

    return SupportResponse(
        conversation_id=(
            conversation_id
        ),

        answer=(
            final_answer
        ),

        sources=(
            sources
        ),
    )


@router.get(
    "/conversations/{conversation_id}",
)
def get_support_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
):

    try:

        history = (
            load_conversation_history(
                db=db,
                conversation_id=(
                    conversation_id
                ),
                limit=50,
            )
        )

    except ValueError:

        raise HTTPException(
            status_code=404,
            detail=(
                "Conversation not found."
            ),
        )

    return {
        "conversation_id":
            conversation_id,

        "message_count":
            len(history),

        "messages":
            history,
    }


@router.get(
    "/conversations/"
    "{conversation_id}/customer-history",
)
def get_conversation_customer_history(
    conversation_id: int,
    db: Session = Depends(get_db),
):

    try:

        history = (
            build_customer_history_context(
                db=db,

                conversation_id=(
                    conversation_id
                ),

                customer_code=None,
                order_number=None,
                ticket_number=None,
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "conversation_id":
            conversation_id,

        "customer_history":
            history,
    }


@router.post(
    "/ask-with-image",
    response_model=SupportResponse,
)
async def ask_support_agent_with_image(
    query: str = Form(
        ...,
        min_length=2,
    ),
    file: UploadFile = File(...),
    conversation_id: int | None = Form(
        default=None,
    ),
    db: Session = Depends(get_db),
):

    if conversation_id is None:

        conversation = (
            start_conversation(
                db=db
            )
        )

    else:

        try:

            conversation = (
                require_conversation(
                    db=db,
                    conversation_id=(
                        conversation_id
                    ),
                )
            )

        except ValueError:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Conversation not found."
                ),
            )

    active_conversation_id = (
        conversation.id
    )

    conversation_history = (
        load_conversation_history(
            db=db,
            conversation_id=(
                active_conversation_id
            ),
            limit=12,
        )
    )

    try:

        image_path = (
            await save_support_image(
                file
            )
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    try:

        vision = (
            analyze_support_image(
                image_path=image_path,
                customer_question=query,
            )
        )

        vision_context = {
            "available": True,
            **vision.model_dump(),
        }

    except Exception:

        vision_context = {
            "available": False,
            "error": (
                "Image analysis was "
                "unavailable."
            ),
        }

    result, _ = (
        invoke_support_graph_observed(
            input_state={
                "user_query":
                    query,

                "conversation_id":
                    active_conversation_id,

                "conversation_history":
                    conversation_history,

                "vision_context":
                    vision_context,
            },

            run_type="support",
        )
    )

    final_answer = (
        result.get(
            "final_answer"
        )
        or (
            "I couldn't generate "
            "a response."
        )
    )

    save_conversation_turn(
        db=db,

        conversation_id=(
            active_conversation_id
        ),

        customer_message=query,

        agent_message=(
            final_answer
        ),
    )

    used_ids = set(
        result.get(
            "citations_used",
            [],
        )
    )

    knowledge_context = (
        result.get(
            "knowledge_context"
        )
        or {}
    )

    knowledge_data = (
        knowledge_context.get(
            "data"
        )
        or {}
    )

    all_citations = (
        knowledge_data.get(
            "citations"
        )
        or []
    )

    sources = []

    for citation in all_citations:

        if (
            citation.get(
                "citation_id"
            )
            not in used_ids
        ):
            continue

        sources.append(
            SupportSource(
                citation_id=(
                    citation[
                        "citation_id"
                    ]
                ),

                document_code=(
                    citation[
                        "document_code"
                    ]
                ),

                document_type=(
                    citation[
                        "document_type"
                    ]
                ),

                version_label=(
                    citation.get(
                        "version_label"
                    )
                ),

                section_title=(
                    citation[
                        "section_title"
                    ]
                ),

                source_filename=(
                    citation[
                        "source_filename"
                    ]
                ),
            )
        )

    return SupportResponse(
        conversation_id=(
            active_conversation_id
        ),

        answer=(
            final_answer
        ),

        sources=(
            sources
        ),
    )