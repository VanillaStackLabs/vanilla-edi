from typing import Any, Type
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

# Schema Imports
from schemas import (
    Outbound997Request,
    Generate810Request,
    Generate810Response,
    Generate856Request,
    Generate856Response,
)
from schemas.po_850 import Generate850Request, Generate850Response

# Generator Imports
from generators.ack_997 import Generator997
from generators.invoice_810 import Invoice810Generator
from generators.asn_856 import ASN856Generator
from generators.po_850 import PO850Generator

router = APIRouter(prefix="/api/v1/generate", tags=["Generators"])


def execute_generator(
    generator_cls: Type[Any],
    payload: BaseModel,
    response_model_cls: Type[BaseModel] | None = None,
    raw: bool = False,
    doc_type: str = "EDI",
) -> Response | BaseModel:
    """
    Executes an X12 EDI generator with unified error handling and response formatting.
    """
    try:
        generator = generator_cls()
        edi_text = generator.generate(payload.model_dump())

        if raw:
            return Response(content=edi_text, media_type="text/plain")

        if response_model_cls:
            return response_model_cls(success=True, edi_content=edi_text)

        return Response(content=edi_text, media_type="text/plain")
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to generate {doc_type} EDI: {str(e)}"
        )


# --- 997 Functional Acknowledgment Routes ---

@router.post(
    "/997",
    summary="Generate Outbound X12 997 Acknowledgment",
    response_class=Response,
)
async def generate_997(request: Outbound997Request):
    return execute_generator(
        Generator997, request, raw=True, doc_type="997"
    )


# --- 810 Invoice Routes ---

@router.post(
    "/810",
    summary="Generate Outbound X12 810 Invoice (JSON Wrapper)",
    response_model=Generate810Response,
)
async def generate_810_invoice(payload: Generate810Request):
    return execute_generator(
        Invoice810Generator,
        payload,
        response_model_cls=Generate810Response,
        doc_type="810",
    )


@router.post(
    "/810/raw",
    summary="Generate Outbound X12 810 Invoice (Raw Text)",
    response_class=Response,
)
async def generate_810_invoice_raw(payload: Generate810Request):
    return execute_generator(
        Invoice810Generator, payload, raw=True, doc_type="810"
    )


# --- 856 Advance Ship Notice (ASN) Routes ---

@router.post(
    "/856",
    summary="Generate Outbound X12 856 ASN (JSON Wrapper)",
    response_model=Generate856Response,
)
async def generate_856_asn(payload: Generate856Request):
    return execute_generator(
        ASN856Generator,
        payload,
        response_model_cls=Generate856Response,
        doc_type="856",
    )


@router.post(
    "/856/raw",
    summary="Generate Outbound X12 856 ASN (Raw Text)",
    response_class=Response,
)
async def generate_856_asn_raw(payload: Generate856Request):
    return execute_generator(
        ASN856Generator, payload, raw=True, doc_type="856"
    )


# --- 850 Purchase Order Routes ---

@router.post(
    "/850",
    summary="Generate Outbound X12 850 Purchase Order (JSON Wrapper)",
    response_model=Generate850Response,
)
async def generate_850_po(payload: Generate850Request):
    """Generates an outbound ANSI X12 850 Purchase Order from JSON."""
    return execute_generator(
        PO850Generator,
        payload,
        response_model_cls=Generate850Response,
        doc_type="850",
    )


@router.post(
    "/850/raw",
    summary="Generate Outbound X12 850 Purchase Order (Raw Text)",
    response_class=Response,
)
async def generate_850_po_raw(payload: Generate850Request):
    """Returns raw text/plain X12 850 EDI content directly for file downloads."""
    return execute_generator(
        PO850Generator, payload, raw=True, doc_type="850"
    )