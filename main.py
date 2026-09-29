import importlib
import pkgutil
from fastapi import FastAPI
import routers

app = FastAPI(
    title="VanillaEDI",
    description="Deployable REST API wrapper that turns legacy X12 EDI into clean JSON.",
    version="1.0.0"
)

# Auto-discover and register all routers inside the routers/ folder
for _, module_name, _ in pkgutil.iter_modules(routers.__path__):
    full_module_name = f"routers.{module_name}"
    module = importlib.import_module(full_module_name)

    # If the module has an APIRouter named 'router', include it
    if hasattr(module, "router"):
        app.include_router(module.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "active", "message": "VanillaEDI server is running."}