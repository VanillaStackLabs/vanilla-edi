import json
import os
import sys

sys.path.insert(0, os.path.abspath("."))

from main import app

output_dir = os.path.join("docs", "api")
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "openapi.json"), "w") as f:
    json.dump(app.openapi(), f, indent=2)