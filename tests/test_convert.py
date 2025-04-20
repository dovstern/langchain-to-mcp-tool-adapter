"""
Tests for the adapter module functionality.
"""

import pytest
from mcp.server import FastMCP
from langchain_to_mcp_tool_adapter import add_langchain_tool_to_server
from langchain_to_mcp_tool_adapter.adapter import reconstruct_func_from_tool
from tests.test_tools import multiply_type_annotation, multiply_pydantic

def test_reconstruct_type_annotation_tool():
    """Test reconstruction of a tool that uses type annotations."""
    reconstructed_tool = reconstruct_func_from_tool(multiply_type_annotation)
    
    # Verify that the reconstructed tool has the expected properties
    assert reconstructed_tool.__name__ == multiply_type_annotation.func.__name__
    assert reconstructed_tool.__doc__ == multiply_type_annotation.description
    
    # Test that the function can be processed by MCP
    from mcp.server.fastmcp.utilities.func_metadata import func_metadata
    metadata = func_metadata(reconstructed_tool)
    assert metadata is not None

def test_reconstruct_pydantic_tool():
    """Test reconstruction of a tool that uses a Pydantic model for args."""
    reconstructed_tool = reconstruct_func_from_tool(multiply_pydantic)
    
    # Verify that the reconstructed tool has the expected properties
    assert reconstructed_tool.__name__ == multiply_pydantic.func.__name__
    assert reconstructed_tool.__doc__ == multiply_pydantic.description
    
    # Test that the function can be processed by MCP
    from mcp.server.fastmcp.utilities.func_metadata import func_metadata
    metadata = func_metadata(reconstructed_tool)
    assert metadata is not None

def test_add_tools_to_server(empty_server, mock_tool, mock_artifact_tool):
    """Test adding tools to a FastMCP server."""
    # Add regular tool
    add_langchain_tool_to_server(empty_server, mock_tool)
    
    # Add artifact tool
    add_langchain_tool_to_server(empty_server, mock_artifact_tool)
    
    # Verify tools were added by checking the server's tool manager
    tools_dict = empty_server._tool_manager._tools
    
    # Tools are registered by their function name, not the Tool name
    # Get the function names from the original tool objects
    simple_func_name = mock_tool.func.__name__
    artifact_func_name = mock_artifact_tool.func.__name__
    
    # Verify both functions are in the tools dictionary
    assert simple_func_name in tools_dict
    assert artifact_func_name in tools_dict
    
    # Verify the tool descriptions were preserved
    assert tools_dict[simple_func_name].description == "A simple mock tool for testing"
    assert tools_dict[artifact_func_name].description == "A mock tool that returns artifacts"