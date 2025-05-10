"""
Tests for adapter.py's artifact response handling.
"""

from langchain_to_mcp_tool_adapter.adapter import handle_artifact_response


def test_handle_regular_response():
    """Test handling of a regular (non-artifact) response."""

    def mock_func(*args, **kwargs):
        return "This is a regular response"

    mock_func.response_format = "text"
    mock_func.__name__ = "mock_func"
    mock_func.__doc__ = "Mock function for testing"

    wrapped = handle_artifact_response(mock_func)

    # Response should pass through unchanged
    result = wrapped("input_param")
    assert result == "This is a regular response"


def test_handle_artifact_response():
    """Test handling of a content_and_artifact response."""

    def mock_artifact_func(*args, **kwargs):
        text = "This is text content"
        artifacts = [
            {
                "type": "file",
                "file": {
                    "filename": "test.png",
                    "file_data": "data:image/png;base64,abcdef123456",
                },
            }
        ]
        return text, artifacts

    # Setup mock properties
    mock_artifact_func.response_format = "content_and_artifact"
    mock_artifact_func.__name__ = "mock_artifact_func"
    mock_artifact_func.__doc__ = "Mock artifact function for testing"

    wrapped = handle_artifact_response(mock_artifact_func)

    # Response should be converted to MCP format
    result = wrapped("input_param")

    # Validate the response format
    assert isinstance(result, tuple)
    assert len(result) == 2  # Text and one file

    # Verify text element
    assert result[0] == "This is text content"

    # Verify file element
    assert result[1].type == "resource"
    assert str(result[1].resource.uri) == "data:image/png;base64,abcdef123456"
    assert result[1].resource.mimeType == "image/png"
    assert result[1].resource.blob == "test.png"


def test_response_metadata_preserved():
    """Test that function metadata is preserved."""

    def mock_func(*args, **kwargs):
        return "Response"

    mock_func.response_format = "text"
    mock_func.__name__ = "original_name"
    mock_func.__doc__ = "original doc"
    mock_func.__annotations__ = {"param": str, "return": str}

    wrapped = handle_artifact_response(mock_func)

    # Metadata should be preserved
    assert wrapped.__name__ == "original_name"
    assert wrapped.__doc__ == "original doc"
    assert wrapped.__annotations__ == {"param": str, "return": str}
