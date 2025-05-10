from langchain.tools import tool
from typing import Annotated, List
from pydantic import BaseModel, Field


# 1. Use type annotations to define the input schema
@tool(
    "multiplication-tool",
)
def multiply_type_annotation(
    a: Annotated[int, "scale factor"],
    b: Annotated[List[int], "list of ints over which to take maximum"],
) -> int:
    """Multiply a by the maximum of b."""
    return a * max(b)


class CalculatorInput(BaseModel):
    a: int = Field(description="first number")
    b: int = Field(description="second number")


@tool("multiplication-tool", args_schema=CalculatorInput)
def multiply_pydantic(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
