import importlib
import pkgutil

# Auto-import all parser modules in this directory on startup
for _, module_name, _ in pkgutil.walk_packages(__path__):
    importlib.import_module(f"{__name__}.{module_name}")