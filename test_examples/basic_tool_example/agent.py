"""
Example of connecting to an MCP server and using a tool with a LangGraph agent.

This file uses langchain-mcp-adapters to connect to the calculator MCP server
and test the tool with a LangGraph agent.
"""
import asyncio
import sys
import os
import argparse
import logging
import time

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

async def run_calculator_agent(model_name="gpt-4o-mini", max_retries=3):
    """
    Connect to the calculator MCP server and test the tool with a LangGraph agent.
    
    Args:
        model_name: Name of the OpenAI model to use
        max_retries: Maximum number of connection retries
    """
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")],
    )
    
    logger.info("Connecting to calculator MCP server via stdio")
    
    # Initialize the model
    model = ChatOpenAI(model=model_name)

    # Set a timeout for the entire operation
    async with asyncio.timeout(60):  
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # Get tools
                tools = await load_mcp_tools(session)
                
                # Create and run the agent
                agent = create_react_agent(model, tools)
                
                # Create a simple test message
                messages = [{"role": "user", "content": "Calculate 10 multiplied by 5"}]
                
                # Run the agent with proper message format
                agent_response = await agent.ainvoke({"messages": messages})
                
                return agent_response

if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test calculator MCP tool with a LangGraph agent")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="OpenAI model to use")
    parser.add_argument("--retries", type=int, default=3, help="Maximum connection retries")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger("httpx").setLevel(logging.DEBUG)
        logging.getLogger("mcp").setLevel(logging.DEBUG)
    
    # Check if OPENAI_API_KEY is set
    if "OPENAI_API_KEY" not in os.environ:
        logger.error("OPENAI_API_KEY environment variable not set.")
        logger.error("Set it with: export OPENAI_API_KEY=your_api_key")
        sys.exit(1)
    
    # Run the agent
    try:
        result = asyncio.run(run_calculator_agent(
            model_name=args.model,
            max_retries=args.retries
        ))
        logger.info(f"Agent response: {result}")
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=args.verbose) 