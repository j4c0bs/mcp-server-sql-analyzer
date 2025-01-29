import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_mcp_decorator():
    """Mock the FastMCP decorator for all tests"""

    def decorator(f):
        return f

    patcher = patch("mcp.server.fastmcp.FastMCP.tool", decorator)
    patcher.start()
    yield
    patcher.stop()
