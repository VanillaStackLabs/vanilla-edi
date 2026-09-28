from fastapi import APIRouter, HTTPException, Response
from schemas import Outbound997Request, Generate810Request, Generate810Response, Generate856Request, Generate856Response
from generators.ack_997 import Generator997
from generators.invoice_810 import Invoice810Generator
from generators.asn_856 import ASN856Generator

router = APIRouter(prefix="/api/v1/generate", tags=["Generators"])

# --- 997 Routes ---
@router.post("/997", summary="Generate Outbound X12 997 Acknowledgment", response_class=Response)
async def generate_997(request: Outbound997Request):
    try:
        generator = Generator997()
        raw_x12 = generator.generate(request.model_dump())
        return Response(content=raw_x12, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 997 EDI: {str(e)}")

# --- 810 Routes ---
@router.post("/810", response_model=Generate810Response)
async def generate_810_invoice(payload: Generate810Request):
    try:
        generator = Invoice810Generator()
        edi_text = generator.generate(payload.model_dump())
        return Generate810Response(success=True, edi_content=edi_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 810 EDI: {str(e)}")

@router.post("/810/raw", response_class=Response)
async def generate_810_invoice_raw(payload: Generate810Request):
    try:
        generator = Invoice810Generator()
        edi_text = generator.generate(payload.model_dump())
        return Response(content=edi_text, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 810 EDI: {str(e)}")

# --- 856 Routes ---
@router.post("/856", response_model=Generate856Response)
async def generate_856_asn(payload: Generate856Request):
    try:
        generator = ASN856Generator()
        edi_text = generator.generate(payload.model_dump())
        return Generate856Response(success=True, edi_content=edi_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 856 EDI: {str(e)}")

@router.post("/856/raw", response_class=Response)
async def generate_856_asn_raw(payload: Generate856Request):
    try:
        generator = ASN856Generator()
        edi_text = generator.generate(payload.model_dump())
        return Response(content=edi_text, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 856 EDI: {str(e)}")

from schemas.po_850 import Generate850Request, Generate850Response
from generators.po_850 import PO850Generator

# --- 850 Routes ---
@router.post("/850", response_model=Generate850Response)
async def generate_850_po(payload: Generate850Request):
    """Generates an outbound ANSI X12 850 Purchase Order from JSON."""
    try:
        generator = PO850Generator()
        edi_text = generator.generate(payload.model_dump())
        return Generate850Response(success=True, edi_content=edi_text)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 850 EDI: {str(e)}")

@router.post("/850/raw", response_class=Response)
async def generate_850_po_raw(payload: Generate850Request):
    """Returns raw text/plain X12 850 EDI content directly for file downloads."""
    try:
        generator = PO850Generator()
        edi_text = generator.generate(payload.model_dump())
        return Response(content=edi_text, media_type="text/plain")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate 850 EDI: {str(e)}")