# -------------------------------------------
# Pre-bootstrap: add src/ to Python path (one-time)
# -------------------------------------------

import sys
from pathlib import Path

# If notebook is in: <project_root>/notebooks/dev
PROJECT_ROOT = Path.cwd().parents[1]
SRC_PATH = PROJECT_ROOT / "src"

if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

print("SRC path active:", SRC_PATH)

# Now imports from src/ will work
from equity_analytics.bootstrap import setup_src_path
setup_src_path()
print("Bootstrap OK")
