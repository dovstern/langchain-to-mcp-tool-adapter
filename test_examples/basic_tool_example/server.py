"""
Example of converting a LangChain calculator tool to an MCP tool.

This file defines and runs an MCP server with a converted LangChain calculator tool.
"""
from langchain.tools import Tool
import uvicorn
import os
import argparse
from mcp.server import FastMCP
from pydantic import BaseModel, Field
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from langchain_to_mcp_tool_adapter import add_langchain_tool_to_server
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("uvicorn").setLevel(logging.DEBUG)
logging.getLogger("fastapi").setLevel(logging.DEBUG)
logging.getLogger("mcp").setLevel(logging.DEBUG)

# Define a Pydantic model for calculator input
class CalculatorInput(BaseModel):
    a: float = Field(description="First number for the operation")
    b: float = Field(description="Second number for the operation")
    operation: str = Field(
        description="Operation to perform (add, subtract, multiply, divide)"
    )

# Define a calculator function
def calculator(a: float, b: float, operation: str) -> str:
    """Perform a basic arithmetic operation between two numbers."""
    try:
        if operation == "add":
            return f"{a} + {b} = {a + b}"
        elif operation == "subtract":
            return f"{a} - {b} = {a - b}"
        elif operation == "multiply":
            return f"{a} * {b} = {a * b}"
        elif operation == "divide":
            if b == 0:
                return "Error: Division by zero"
            return f"{a} / {b} = {a / b}"
        else:
            return f"Invalid operation: {operation}. Please use add, subtract, multiply, or divide."
    except Exception as e:
        return f"Error: {str(e)}"

# Create a LangChain calculator tool
calculator_tool = Tool(
    name="calculator",
    description="A calculator that can perform basic arithmetic operations between two numbers",
    func=calculator,
    args_schema=CalculatorInput
)

# Create an MCP server with explicit SSE support
app = FastMCP(title="Calculator API", add_sse=True)

# Add the LangChain calculator tool to the MCP server
add_langchain_tool_to_server(app, calculator_tool)

if __name__ == "__main__":
    app.run(transport="stdio") 