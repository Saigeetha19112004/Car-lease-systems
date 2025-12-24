"""Export the FastAPI OpenAPI schema to docs/openapi.json"""
import json
from pathlib import Path

from app.main import app

OUT = Path(__file__).resolve().parent.parent / 'docs' / 'openapi.json'
OUT.parent.mkdir(parents=True, exist_ok=True)
with OUT.open('w', encoding='utf-8') as f:
    json.dump(app.openapi(), f, indent=2)
print(f'Wrote OpenAPI schema to {OUT}')
