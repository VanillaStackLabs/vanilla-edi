import importlib
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import main

client = TestClient(main.app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "active", "message": "VanillaEDI server is running."}

def test_auto_discover_routers_missing_router_attribute():
    """
    Tests the False branch of the hasattr(module, 'router') check in main.py
    by simulating a module in the routers/ folder that has no router attribute.
    """
    mock_module = MagicMock()
    del mock_module.router  # Ensure hasattr(module, "router") evaluates to False

    # Mock iter_modules to yield a fake module, and import_module to return our mock
    with patch("pkgutil.iter_modules", return_value=[(None, "fake_no_router", False)]):
        with patch("importlib.import_module", return_value=mock_module):
            # Reload main.py so the module-level auto-discovery loop re-executes
            importlib.reload(main)

    # Restore main.py to its normal state so the real routers are reloaded
    importlib.reload(main)