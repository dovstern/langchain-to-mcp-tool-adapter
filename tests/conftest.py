"""
Configuration and fixtures for pytest.
"""

import pytest
from mcp.server import FastMCP
from langchain.tools import Tool


@pytest.fixture
def empty_server():
    """Return a fresh FastMCP server instance."""
    return FastMCP()


@pytest.fixture
def mock_tool():
    """Return a simple mock LangChain tool."""

    def simple_func(text: str) -> str:
        return f"Processed: {text}"

    return Tool(
        name="mock_tool",
        description="A simple mock tool for testing",
        func=simple_func,
    )


@pytest.fixture
def mock_artifact_tool():
    """Return a mock LangChain tool that returns artifacts."""

    def artifact_func(text: str) -> tuple:
        content = f"Generated content for: {text}"
        base64_image = (
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYA"
            "AAAAYAAjCB0C8AAAAASUVORK5CYII="
        )

        artifacts = [
            {
                "type": "file",
                "file": {
                    "filename": "test.png",
                    "file_data": f"data:image/png;base64,{base64_image}",
                },
            }
        ]

        return content, artifacts

    tool = Tool(
        name="mock_artifact_tool",
        description="A mock tool that returns artifacts",
        func=artifact_func,
        response_format="content_and_artifact",
    )

    return tool
