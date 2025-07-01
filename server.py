import sys
from pathlib import Path

from src.api import app

sys.path.append(str(Path(__file__).parent))
print(str(Path(__file__).parent))
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
