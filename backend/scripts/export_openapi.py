"""openapi.yaml を docs/ に書き出すスクリプト。

使い方:
    cd backend && python scripts/export_openapi.py
"""
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app  # noqa: E402

schema = app.openapi()
output = Path(__file__).parent.parent / "docs" / "openapi.yaml"
output.parent.mkdir(exist_ok=True)

with open(output, "w", encoding="utf-8") as f:
    yaml.dump(schema, f, allow_unicode=True, sort_keys=False)

print(f"Written: {output}")
