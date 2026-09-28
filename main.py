from fastapi import FastAPI
from routers.parse import router as parse_router
from routers.generate import router as generate_router

app = FastAPI(
    title="VanillaEDI",
    description="Deployable REST API wrapper that turns legacy X12 EDI into clean JSON.",
    version="1.0.0"
)

# Register Routers
app.include_router(parse_router)
app.include_router(generate_router)

@app.get("/", tags=["Health"])
def health_check():
    return {"status": "active", "message": "VanillaEDI server is running."}