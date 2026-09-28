from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from schemas import EDIDocumentSchema
from edi_parser import parse_x12_to_dict
from services.webhooks import dispatch_webhook

router = APIRouter(prefix="/api/v1", tags=["Parser"])

@router.post("/parse", response_model=EDIDocumentSchema, summary="Parse X12 EDI File to JSON")
async def parse_edi(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    webhook_url: str = Form(None, description="Optional URL to forward the parsed JSON to")
):
    try:
        content = await file.read()
        raw_edi_string = content.decode("utf-8")
        parsed_data = parse_x12_to_dict(raw_edi_string)

        if webhook_url:
            background_tasks.add_task(dispatch_webhook, webhook_url, parsed_data)

        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse EDI payload: {str(e)}")