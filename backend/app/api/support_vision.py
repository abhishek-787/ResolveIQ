from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.schemas.vision import (
    VisionAnalysisResult,
)

from app.services.support_image_storage import (
    save_support_image,
)

from app.services.vision_analysis import (
    analyze_support_image,
)

from app.schemas.vision_grounding import (
    VisionGroundingResult,
)

from app.services.vision_grounding import (
    ground_vision_case,
)

router = APIRouter(
    prefix="/support/vision",
    tags=["Support Vision"],
)

@router.post(
    "/analyze",
    response_model=VisionAnalysisResult,
)
async def analyze_uploaded_image(
    file: UploadFile = File(...),

    question: str | None = Form(
        default=None
    ),
):

    try:

        image_path = (
            await save_support_image(
                file
            )
        )

        result = (
            analyze_support_image(
                image_path=image_path,
                customer_question=question,
            )
        )

        return result

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Vision analysis failed: "
                f"{exc}"
            ),
        )

@router.post(
    "/ground",
    response_model=VisionGroundingResult,
)
async def ground_support_image(
    file: UploadFile = File(...),

    question: str = Form(
        ...,
        min_length=2,
    ),

    order_number: str | None = Form(
        default=None,
    ),

    use_mock_vision: bool = Form(
        default=False,
    ),
):

    try:

        image_path = (
            await save_support_image(
                file
            )
        )

        return ground_vision_case(
            image_path=image_path,

            question=question,

            order_number=(
                order_number
            ),

            use_mock_vision=(
                use_mock_vision
            ),
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Vision grounding failed: "
                f"{exc}"
            ),
        )