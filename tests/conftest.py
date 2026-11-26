import sys
from pathlib import Path
import pytest

# Add backend directory to sys.path for all tests
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session")
def anyio_backend():
    """Restrict anyio tests to asyncio only (trio not installed)."""
    return "asyncio"


