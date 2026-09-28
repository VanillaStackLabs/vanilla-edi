from fastapi import FastAPI, UploadFile, File, HTTPException, Response, BackgroundTasks, Form
from schemas import EDIDocumentSchema, Outbound997Request
from generators.ack_997 import Generator997
from edi_parser import parse_x12_to_dict
from services.webhooks import dispatch_webhook

app = FastAPI(
    title="VanillaEDI",
    description="Deployable REST API wrapper that turns legacy X12 EDI into clean JSON.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "active", "message": "VanillaEDI server is running."}


@app.post("/api/v1/parse", response_model=EDIDocumentSchema, summary="Parse X12 EDI File to JSON")
async def parse_edi(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(...),
        webhook_url: str = Form(None, description="Optional URL to forward the parsed JSON to")
):
    try:
        content = await file.read()
        raw_edi_string = content.decode("utf-8")
        parsed_data = parse_x12_to_dict(raw_edi_string)

        # If a webhook URL is provided, queue the dispatch task to run after the response is sent
        if webhook_url:
            background_tasks.add_task(dispatch_webhook, webhook_url, parsed_data)

        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse EDI payload: {str(e)}")

@app.post(
    "/api/v1/generate/997",
    summary="Generate Outbound X12 997 Acknowledgment",
    response_class=Response
)
async def generate_997(request: Outbound997Request):
    try:
        generator = Generator997()
        raw_x12 = generator.generate(request.model_dump())
        return Response(content=raw_x12, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 997 EDI: {str(e)}")