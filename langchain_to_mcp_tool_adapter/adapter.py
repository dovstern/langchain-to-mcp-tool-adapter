from mcp.server import FastMCP
from langchain.tools import Tool
import re
import functools
from mcp.types import ImageContent, EmbeddedResource, BlobResourceContents


def reconstruct_func_from_tool(tool: Tool):
    """
    Reconstructs a function from a LangChain tool to be compatible with MCP.

    Args:
        tool: A LangChain Tool instance

    Returns:
        A function that can be registered with MCP
    """
    func = tool.func
    description = tool.description
    args_schema = tool.args_schema

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    # Override with tool-specific attributes
    if description is not None:
        wrapper.__doc__ = description

    # Add args schema data if needed
    if args_schema is not None and not hasattr(wrapper, "__annotations__"):
        wrapper.__annotations__ = args_schema.model_json_schema()

    # Copy the response_format attribute if it exists
    if hasattr(tool, "response_format"):
        wrapper.response_format = tool.response_format

    return wrapper


def _extract_mime_type(data_uri):
    """
    Extract the MIME type from a data URI.

    Args:
        data_uri: A data URI string (e.g., "data:image/png;base64,...")

    Returns:
        The MIME type as a string, or None if not found
    """
    match = re.match(r"data:([^;]+);base64,", data_uri)
    if match:
        return match.group(1)
    return None


def handle_artifact_response(func):
    """
    If langchain tool response_format=="content_and_artifact", then the tool
    returns a tuple of (text, artifacts), whereas MCP expects a dictionary
    with a "content" key and a combination of text and file artifacts.
    This function adapts the tool's response to the MCP expected format.

    Args:
        func: A function that may return content_and_artifact format

    Returns:
        A function that converts LangChain artifact format to MCP format
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Check if this is an artifact-returning function
        has_response_format = hasattr(func, "response_format")
        is_artifact = (
            has_response_format and func.response_format == "content_and_artifact"
        )

        if is_artifact:
            text, artifacts = func(*args, **kwargs)
            # init a list (will be converted to a tuple)
            response = [text]

            for artifact in artifacts:
                if artifact["type"] == "image_url":
                    file_data = artifact["image_url"]["url"]
                    mime_type = _extract_mime_type(file_data)
                    response.append(
                        ImageContent(type="image", data=file_data, mimeType=mime_type)
                    )
                elif artifact["type"] == "file":
                    file_data = artifact["file"]["file_data"]
                    mime_type = _extract_mime_type(file_data)
                    file_name = artifact["file"]["filename"]
                    response.append(
                        EmbeddedResource(
                            type="resource",
                            resource=BlobResourceContents(
                                blob=file_name,
                                uri=file_data,
                                mimeType=mime_type,
                            ),
                        )
                    )

            return tuple(response)
        else:
            return func(*args, **kwargs)

    # Ensure response_format attribute is preserved
    if hasattr(func, "response_format"):
        wrapper.response_format = func.response_format

    return wrapper


def add_langchain_tool_to_server(server: FastMCP, tool: Tool):
    """
    Adds a LangChain tool to a FastMCP server.

    Args:
        server: A FastMCP server instance
        tool: A LangChain Tool instance

    Returns:
        None
    """

    # First reconstruct the function from the LangChain tool
    func = reconstruct_func_from_tool(tool)

    # Wrap it to handle artifact responses
    func = handle_artifact_response(func)

    # Add the tool to the server
    server.add_tool(func)
