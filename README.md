# LangChain Tool to MCP Adapter

[![PyPI version](https://badge.fury.io/py/langchain-tool-to-mcp-adapter.svg)](https://badge.fury.io/py/langchain-tool-to-mcp-adapter)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

![@LangChain Tool to MCP Adapter](@LangChain%20Tool%20to%20MCP%20Adapter.png)

Convert your LangChain/LangGraph tools to Model Context Protocol with just one line of code. This adapter bridges the gap between LangChain and MCP ecosystems, making your tools available to both without duplicating code or tool metadata.

## What are LLM "tools"?

AI agents today go beyond chat, using LLMs to call tools — functions that interact with the outside world (applications, APIs, database, browsers). LangChain and Model Context Protocol (MCP) both offer interfaces for exposing these tools to LLMs, but with different strengths:

- **LangChain tools** are optimized for LangGraph, the widely adopted agent development framework (why spin up an MCP Server for a tool you could just run from the code?).
- **MCP tools** are designed for interoperability, making them discoverable by MCP client applications like Claude, Cursor, and soon ChatGPT.

While LangChain already provides an MCP → LangGraph adapter, this package provides the missing piece for LangChain-first developers.

## Why Use This Package?

- **Build Once, Use Everywhere**: Make your tools available in both LangChain and MCP implementations without duplicating code.
- **Handle Artifacts Properly**: Automatic conversion between LangChain's `content_and_artifact` format and MCP's content format for images, PDFs, and other binary data.
- **Preserve Metadata**: Tool descriptions, argument schemas, and other metadata are preserved during conversion - critical for agents to understand how to use your tools.

## Installation

```bash
pip install langchain-tool-to-mcp-adapter
```

## Quick Start

```python
from mcp.server import FastMCP
from langchain.tools import Tool
from langchain_tool_to_mcp_adapter import add_langchain_tool_to_server

# Create a LangChain tool
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b

calculator_tool = Tool(
    name="calculator",
    description="Multiply two numbers together",
    func=multiply
)

# Create a FastMCP server and add the tool with just one line
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
