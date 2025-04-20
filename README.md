# LangChain to MCP Tool Adapter

[![PyPI version](https://badge.fury.io/py/langchain-to-mcp-tool-adapter.svg)](https://badge.fury.io/py/langchain-to-mcp-tool-adapter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python package for converting LangChain tools to FastMCP tools, making it easy to use your existing LangChain tools with Anthropic's MCP server.

## Why Use This Package?

- **Simpler Implementation**: While LangChain offers an MCP-to-LangChain adapter, it requires a running MCP server either remotely or co-located with an agent, which can be finicky. LangChain tools have a simpler implementation and are more lightweight.
- **Use in Multiple Environments**: When creating tools (especially for open source), you might want to make them available in both LangChain and MCP implementations without duplicating code.
- **Handle Artifacts Properly**: Automatic conversion between LangChain's `content_and_artifact` format and MCP's content format for images, PDFs, and other binary data.
- **Preserve Metadata**: Tool descriptions, argument schemas, and other metadata are preserved during conversion.

## Installation

```bash
pip install langchain-to-mcp-tool-adapter
```

## Quick Start

```python
from mcp.server import FastMCP
from langchain.tools import Tool
from langchain_to_mcp_tool_adapter import add_langchain_tool_to_server

# Create a LangChain tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator_tool = Tool(
    name="calculator",
    description="Multiply two numbers together",
    func=multiply
)

# Create a FastMCP server and add the tool
server = FastMCP()
add_langchain_tool_to_server(server, calculator_tool)

# Run the server
server.run()
```

## Working with Argument Schemas

### Type Annotations

```python
from typing import Annotated, List
from langchain.tools import tool

@tool("multiplication-tool")
def multiply_type_annotation(
    a: Annotated[int, "The scale factor to multiply by"],
    b: Annotated[List[int], "A list of integers to find the maximum from"]
) -> int:
    """Multiply a by the maximum value in list b."""
    return a * max(b)

# Add to MCP server
add_langchain_tool_to_server(server, multiply_type_annotation)
```

### Pydantic Models

```python
from pydantic import BaseModel, Field
from langchain.tools import tool

class CalculatorInput(BaseModel):
    a: int = Field(description="The first number to multiply")
    b: int = Field(description="The second number to multiply")

@tool("multiplication-tool", args_schema=CalculatorInput)
def multiply_pydantic(a: int, b: int) -> int:
    """Multiply two numbers together."""
    return a * b

# Add to MCP server
add_langchain_tool_to_server(server, multiply_pydantic)
```

## Working with Artifacts (Images, PDFs, etc.)

This adapter seamlessly handles LangChain tools that return artifacts like images or PDFs:

```python
from langchain.tools import Tool

def generate_image(prompt: str) -> tuple:
    # Generate an image (mocked here)
    image_data = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
    
    # Return in LangChain's content_and_artifact format
    content = f"Generated image for: {prompt}"
    artifacts = [{
        "type": "file",
        "file": {
            "filename": "generated.png",
            "file_data": image_data,
        }
    }]
    
    return content, artifacts

# Create the tool with content_and_artifact response format
image_tool = Tool(
    name="image_generator",
    description="Generates an image based on a text prompt",
    func=generate_image,
    response_format="content_and_artifact"
)

# Add to MCP server - artifacts will be properly converted
add_langchain_tool_to_server(server, image_tool)
```

## Supported Tool Features

- ✅ Type-annotated tools
- ✅ Pydantic schema tools
- ✅ Regular string/JSON output
- ✅ Image and PDF artifacts
- ✅ Tool descriptions and metadata

## How It Works

The adapter performs these key operations:
1. Reconstructs the function from the LangChain tool, preserving metadata
2. Handling tool responses like images PDFs: Adapts between LangChain's non-standard `content_and_artifact` tuple format and MCP's more standard content structure that aligns with LLM provider APIs (this is crucial for binary artifacts like images and PDFs)
3. Registers the converted function with the FastMCP server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
