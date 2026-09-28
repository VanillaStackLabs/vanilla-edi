from fastapi import FastAPI, UploadFile, File, HTTPException
from schemas import EDIDocumentSchema
from edi_parser import parse_x12_to_dict

app = FastAPI(
    title="VanillaEDI",
    description="Deployable REST API wrapper that turns legacy X12 EDI into clean JSON.",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "active", "message": "VanillaEDI server is running."}

@app.post("/api/v1/parse", response_model=EDIDocumentSchema, summary="Parse X12 EDI File to JSON")
async def parse_edi(file: UploadFile = File(...)):
    try:
        content = await file.read()
        raw_edi_string = content.decode("utf-8")
        parsed_data = parse_x12_to_dict(raw_edi_string)
        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse EDI payload: {str(e)}")

