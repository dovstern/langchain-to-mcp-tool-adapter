from mcp.server import FastMCP
from langchain.tools import Tool
import re

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
    
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    wrapper.__name__ = func.__name__
    if description is not None:
        wrapper.__doc__ = description
    if args_schema is not None:
        wrapper.__annotations__ = args_schema.model_json_schema()
    
    # Copy the response_format attribute if it exists
    if hasattr(tool, 'response_format'):
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
    match = re.match(r'data:([^;]+);base64,', data_uri)
    if match:
        return match.group(1)
    return None

def handle_artifact_response(func):
    '''
    If langchain tool response_format=="content_and_artifact", then the tool returns a tuple of (text, artifacts), 
    whereas MCP expects a dictionary with a "content" key and a combination of text and file artifacts.
    This function adapts the tool's response to the MCP expected format.
    
    Args:
        func: A function that may return content_and_artifact format
        
    Returns:
        A wrapped function that converts LangChain artifact format to MCP format
    '''
    def wrapper(*args, **kwargs):
        # Check if this is an artifact-returning function
        has_response_format = hasattr(func, 'response_format')
        is_artifact = has_response_format and func.response_format == "content_and_artifact"
        
        if is_artifact:
            text, artifacts = func(*args, **kwargs)
            response = {
                "content": [
                    {
                        "type": "text",
                        "text": text
                    }   
                ]
            }
            
            for artifact in artifacts:
                # response["content"].append({
                #     "type": "file",
                #     "data": artifact.data,
                #     "mimeType": artifact.mime_type
                # })
                if artifact["type"] == "file":
                    file_data = artifact["file"]["file_data"]
                    mime_type = _extract_mime_type(file_data)
                    
                    response["content"].append({
                        "type": "file",
                        "data": file_data,
                        "mimeType": mime_type
                    })
            
            return response
        else:
            return func(*args, **kwargs)
    
    # Preserve function metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    if hasattr(func, '__annotations__'):
        wrapper.__annotations__ = func.__annotations__
    if hasattr(func, 'response_format'):
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
    func = reconstruct_func_from_tool(tool)
    func = handle_artifact_response(func)
    server.add_tool(func)

