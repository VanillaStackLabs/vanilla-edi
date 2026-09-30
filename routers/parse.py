from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Form
from fastapi.responses import StreamingResponse
from schemas import EDIDocumentSchema
from edi_parser import parse_x12_to_dict
from services.webhooks import dispatch_webhook
from parsers.stream import EDIStreamParser

router = APIRouter(prefix="/api/v1/parse", tags=["Parser"])

@router.post("", response_model=EDIDocumentSchema, summary="Parse X12 EDI File to JSON")
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

async def process_edi_stream(file: UploadFile):
    """Generator function that yields JSON-Lines back to the client."""
    parser = EDIStreamParser(file)

    try:
        async for segment in parser.stream_segments():
            elements = segment.split(parser.element_sep)

            if elements[0] == "ST":
                yield f'{{"event": "transaction_start", "type": "{elements[1]}"}}\n'
            elif elements[0] == "SE":
                yield f'{{"event": "transaction_end"}}\n'
            else:
                yield f'{{"segment": "{elements[0]}", "element_count": {len(elements) - 1}}}\n'

    except ValueError as e:
        yield f'{{"error": "{str(e)}"}}\n'

@router.post("/stream", summary="Stream Parse Massive X12 EDI Files")
async def stream_large_edi(file: UploadFile = File(...)):
    """
    Parses massive batch EDI files with near-zero memory footprint.
    Streams the parsed results back as JSON-Lines.
    """
    return StreamingResponse(process_edi_stream(file), media_type="application/x-ndjson")