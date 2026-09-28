# VanillaEDI

> A quick and easily deployed, stateless REST API microservice that converts legacy ANSI X12 EDI into clean, developer-friendly JSON.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python 3.14+](https://img.shields.io/badge/python-3.14+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

VanillaEDI bridges modern supply chain software with legacy EDI standard formats (ANSI X12). Built on FastAPI and Pydantic, it provides an instant HTTP endpoint to parse EDI files into structured JSON or dispatch them asynchronously to internal webhooks.

---

## Key Features

- Zero-Config Parsing: Supports 850 (Purchase Orders), 810 (Invoices), 856 (Advance Ship Notices), and 997 (Functional Acknowledgments).
- Async Webhook Dispatcher: Automatically forwards parsed JSON to your ERP or internal microservices in the background.
- Resilient Fallbacks: Inferred transaction detection handles non-standard delimiters and malformed header tags seamlessly.
- Outbound 997 Generator: Instantly build compliant X12 997 response files via simple JSON payloads.
- Docker Ready: Deploy as an isolated stateless container in seconds.

---

## Quickstart

### Running with Docker

```bash
docker build -t vanilla-edi .
docker run -p 8000:8000 vanilla-edi
```

Your API is now live at http://localhost:8000.

Interactive Swagger documentation is available at http://localhost:8000/docs.

---
## API Usage Examples
### 1. Parse an EDI File to JSON
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/parse' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample_850.edi'
```
### Response (200 OK):
```json
{
  "transaction_type": "850",
  "sender_id": "WALMART",
  "receiver_id": "MYCOMPANY",
  "control_number": "000000001",
  "po_number": "PO-998231",
  "po_date": "20260928",
  "ship_to": {
    "name": "BUFFALO DISTRO CENTER",
    "city": "BUFFALO",
    "state": "NY",
    "zip": "14201"
  },
  "line_items": [
    {
      "line_number": "001",
      "quantity": 500,
      "price": 12.5,
      "sku": "WIDGET-BLUE",
      "description": "BLUE INDUSTRIAL WIDGET"
    }
  ]
}
```
### 2. Generate an Outbound EDI File (Raw text/plain)
Easily generate outbound documents like an 810 Invoice by hitting a generator's `/raw` endpoint.
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/generate/810/raw' \
  -H 'Content-Type: application/json' \
  -d '{
    "invoice_number": "INV-9901",
    "sender_id": "MYCOMPANY",
    "receiver_id": "WALMART",
    "line_items": [
      {
        "line_number": "1",
        "quantity": 500,
        "price": 12.5,
        "sku": "WIDGET-BLUE"
      }
    ]
  }'
```


### 3. Parse & Dispatch to an ERP Webhook
Pass an optional `webhook_url` parameter to asynchronously push the JSON to your internal database or processing pipeline:
```bash
curl -X 'POST' \
  'http://localhost:8000/api/v1/parse' \
  -F 'file=@sample_850.edi' \
  -F 'webhook_url=https://erp.internal.company.com/api/v1/edi-ingest'
```
---
## Running Tests
VanillaEDI maintains strict test coverage across parser units, utility formatters, generators, and API endpoints:

```bash
pip install -r requirements.txt
pytest
```
---
## License
Distributed under the MIT License. See `LICENSE` for more information.