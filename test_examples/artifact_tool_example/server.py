"""
Example of converting a LangChain tool that returns artifacts to an MCP tool.

This file defines and runs an MCP server with a converted LangChain tool that returns text and an image.
"""
from langchain.tools import Tool
from pydantic import BaseModel, Field
from mcp.server import FastMCP
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain_to_mcp_tool_adapter import add_langchain_tool_to_server
import base64
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("mcp").setLevel(logging.DEBUG)

# Define a Pydantic model for the tool's arguments
class ImageRequestInput(BaseModel):
    """Input for the image request tool."""
    show_logo: bool = Field(
        description="Whether to show the MCP logo image",
        default=True
    )

class PDFRequestInput(BaseModel):
    """Input for the PDF request tool."""
    include_summary: bool = Field(
        description="Whether to include a summary with the PDF",
        default=True
    )

def get_image_data(image_path):
    """Get base64 encoded image data from a file path."""
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_string

def get_file_data(file_path):
    """Get base64 encoded data from a file path."""
    with open(file_path, "rb") as file:
        encoded_string = base64.b64encode(file.read()).decode("utf-8")
    return encoded_string

# Create a function that returns text and an image
def get_mcp_logo(show_logo: bool = True):
    """Return the MCP logo and a description."""
    content = "Here is a picture of the Model Context Protocol (MCP) logo."
    
    if not show_logo:
        return content
    
    # Get the path to the MCP logo image
    current_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(current_dir, "mcp.jpeg")
    
    # Encode the image
    encoded_image = get_image_data(image_path)
    image_data_uri = f"data:image/jpeg;base64,{encoded_image}"
    
    # Create the artifacts list
    artifacts = [{
        "type": "image_url",
        "image_url": {
            "url": image_data_uri
        }
    }]
    
    # Return the content and artifacts
    return content, artifacts

# Create a function that returns a PDF document
def get_agents_guide(include_summary: bool = True):
    """Return the 'A Practical Guide to Building Agents' PDF."""
    content = "Here is 'A Practical Guide to Building Agents' PDF."
    
    if include_summary:
        content += " This document provides comprehensive guidance on designing and implementing AI agents."
    
    # Get the path to the PDF file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, "a-practical-guide-to-building-agents.pdf")
    
    # Encode the PDF
    encoded_pdf = get_file_data(pdf_path)
    pdf_data_uri = f"data:application/pdf;base64,{encoded_pdf}"
    
    # Create the artifacts list
    artifacts = [{
        "type": "file",
        "file": {
            "filename": "a-practical-guide-to-building-agents.pdf",
            "file_data": pdf_data_uri
        }
    }]
    
    # Return the content and artifacts
    return content, artifacts

# Create a LangChain tool with artifact response
mcp_logo_tool = Tool(
    name="get_mcp_logo",
    description="Get the MCP logo image.",
    func=get_mcp_logo,
    args_schema=ImageRequestInput,
    response_format="content_and_artifact"  # Important: specify artifact response format
)

# Create a LangChain tool for the PDF guide
agents_guide_tool = Tool(
    name="get_agents_guide",
    description="Get the 'A Practical Guide to Building Agents' PDF document.",
    func=get_agents_guide,
    args_schema=PDFRequestInput,
    response_format="content_and_artifact"  # Important: specify artifact response format
)

# Create an MCP server with explicit SSE support
app = FastMCP(title="MCP Logo API", add_sse=True)

# Add the LangChain tools to the MCP server
add_langchain_tool_to_server(app, mcp_logo_tool)
add_langchain_tool_to_server(app, agents_guide_tool)

if __name__ == "__main__":
    app.run(transport="stdio") 