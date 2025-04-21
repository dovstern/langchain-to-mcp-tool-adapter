"""
Example of connecting to an MCP server and using an artifact tool with a LangGraph agent.

This file uses langchain-mcp-adapters to connect to the MCP logo MCP server
and test the artifact tool with a LangGraph agent.
"""
import asyncio
import sys
import os
import argparse
import logging
import time
from examples.mcp_to_langchain_utils import convert_artifacts_to_human_message, convert_mcp_artifact_types_to_langchain

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

async def run_mcp_logo_agent(model_name="gpt-4o-mini", max_retries=3):
    """
    Connect to the MCP logo MCP server and test the tool with a LangGraph agent.
    
    Args:
        model_name: Name of the OpenAI model to use
        max_retries: Maximum number of connection retries
    """
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=[os.path.join(os.path.dirname(os.path.abspath(__file__)), "server.py")],
    )
    
    logger.info("Connecting to MCP logo server via stdio")
    
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
                tool_dict = {tool.name: tool for tool in tools}

                
                # Create a simple test message
                from langchain_core.messages import HumanMessage, ToolCall
                messages = [HumanMessage(content="Get the MCP logo and the Practical Guide to Building Agents PDF and then summarize what you saw / read.")]
                llm_response = await model.bind_tools(tools).ainvoke(messages)
                messages.append(llm_response)
                if llm_response.tool_calls:
                    tool_messages = []
                    for tool_call in llm_response.tool_calls:
                        tool_call_obj = ToolCall(**tool_call)
                        tool_message = await tool_dict[tool_call_obj['name']].ainvoke(tool_call_obj)
                        tool_messages.append(convert_mcp_artifact_types_to_langchain(tool_message))
                    messages.extend(tool_messages)
                    # Human Messages must come after the tool messages are added to the messages list
                    for tool_message in tool_messages:
                        if tool_message.artifact:
                            tool_artifact_human_message = convert_artifacts_to_human_message(tool_message)
                            messages.append(tool_artifact_human_message)
                else:
                    raise Exception("No tool call found in the response")

                messages += [
                    HumanMessage(content="Summarize what you saw / read.")
                ]
                
                agent_response = await model.ainvoke(messages)

                return agent_response.content

if __name__ == "__main__":
    # langsmith trace
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    # project
    os.environ["LANGCHAIN_PROJECT"] = "onboarding"
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Test MCP logo tool with a LangGraph agent")
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
        result = asyncio.run(run_mcp_logo_agent(
            model_name=args.model,
            max_retries=args.retries
        ))
        logger.info(f"Agent response: {result}")
    except Exception as e:
        logger.error(f"Error running agent: {e}", exc_info=args.verbose) 