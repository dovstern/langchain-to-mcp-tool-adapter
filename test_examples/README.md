# LangChain Tool to MCP Adapter Examples

This directory contains examples demonstrating how to convert LangChain tools to MCP tools using the adapter.

## Bidirectional Conversion Testing

These examples specifically demonstrate the full bidirectional conversion cycle (LangChain → MCP → LangChain) to validate the adapter's interoperability. While this complete round-trip conversion isn't typical for most production use cases, it serves as an excellent test to ensure:

1. The adapter correctly preserves all tool metadata, argument schemas, and response formats
2. Tools can be seamlessly converted between ecosystems without information loss
3. Both standard and artifact-returning tools work correctly across the conversion boundaries

In real-world scenarios, you would typically only convert in one direction based on your needs (LangChain to MCP or vice versa), but these examples confirm that bidirectional conversion works correctly when needed.

## Prerequisites

Before running these examples, ensure you have installed the necessary dependencies:

```bash
pip install -e ..  # Install the langchain-tool-to-mcp-adapter from the parent directory
pip install langchain uvicorn fastapi  # Required dependencies
```

For testing with langchain-mcp-adapters, you'll need additional dependencies:

```bash
pip install langchain-mcp-adapters langgraph langchain-openai httpx
```

You can also install all development dependencies at once:

```bash
pip install -e ".[dev]"
```

## Directory Structure

- **agent_test_utils.py**: Common utility functions for testing MCP tools with langchain-mcp-adapters
- **basic_tool_example/**: Example with a basic calculator tool
  - **server.py**: MCP server with a calculator tool
  - **agent.py**: Agent that connects to the server and tests the tool
- **artifact_tool_example/**: Example with a tool that returns text and an image
  - **server.py**: MCP server with an artifact-returning tool
  - **agent.py**: Agent that connects to the server and tests the tool
  - **mcp.jpeg**: Sample image used by the artifact tool example

## Running the Examples

Each example has been split into separate server and agent components that should be run in different terminals.

### 1. Basic Tool Example

**Terminal 1**: Start the MCP server
```bash
cd examples
python basic_tool_example/server.py
```

**Terminal 2**: Run the agent to test the tool
```bash
cd examples
export OPENAI_API_KEY=your_api_key
python basic_tool_example/agent.py
```

### 2. Artifact Tool Example

**Terminal 1**: Start the MCP server
```bash
cd examples
python artifact_tool_example/server.py
```

**Terminal 2**: Run the agent to test the tool
```bash
cd examples
export OPENAI_API_KEY=your_api_key
python artifact_tool_example/agent.py
```

## Testing with Customization

Both the server and agent scripts accept command-line options:

### Server Options

```bash
python basic_tool_example/server.py --port 8000
python artifact_tool_example/server.py --port 8001
```

### Agent Options

```bash
# Basic options
python basic_tool_example/agent.py --port 8000 --model gpt-4

# With debugging enabled
python artifact_tool_example/agent.py --port 8001 --model gpt-4 --verbose --retries 5
```

## Connection Details

The agent scripts use Server-Sent Events (SSE) to connect to the MCP server. The langchain-mcp-adapters library requires this transport method - it only supports 'sse' or 'stdio' transports.

When connecting, the agent will use the SSE endpoint of the server:
```
http://localhost:8000/sse
```

## Troubleshooting

If you encounter errors when running the agent, try these solutions:

1. **Connection errors (500 Internal Server Error)**:
   - Make sure you're using the latest version of the code with SSE explicitly enabled
   - Run the server with verbose logging: `python basic_tool_example/server.py`
   - Run the agent with verbose logging: `python basic_tool_example/agent.py --verbose`
   - Try increasing the retry count: `python basic_tool_example/agent.py --retries 5`
   - Add additional delay before connecting: Modify the `time.sleep()` value in the agent code

2. **Verifying SSE Endpoint**:
   - After starting the server, manually test the SSE endpoint using curl:
     ```bash
     curl -N http://localhost:8000/sse
     ```
   - You should see data streaming rather than an immediate error

3. **Missing OpenAI API key**:
   - Make sure to set your OpenAI API key: `export OPENAI_API_KEY=your_api_key`

4. **Missing dependencies**:
   - Install all required packages with: `pip install -e ".[dev]"`
   - Ensure you have httpx installed: `pip install httpx`

5. **Library Compatibility**:
   - The examples require specific MCP server implementation details
   - Make sure you're using compatible versions of fastmcp and langchain-mcp-adapters

## How It Works

The examples demonstrate the full conversion cycle for testing purposes:

1. **Start with a LangChain tool**: We begin with a standard LangChain tool (either returning simple values or artifacts)
2. **Convert to MCP**: The LangChain tool is converted to an MCP tool using our adapter
3. **Expose via MCP server**: The converted MCP tool is exposed through a FastAPI server with SSE support
4. **Convert back to LangChain**: The agent connects to the server using langchain-mcp-adapters over SSE, effectively converting the tool back to LangChain
5. **Test with an agent**: Finally, a LangGraph agent uses the reconverted tool to perform tasks

This round-trip approach provides a robust test of the adapter's capabilities while also resolving practical issues with running the server and agent in the same process.

While this full cycle is primarily for testing and demonstration, it validates that the adapter preserves all necessary metadata and functionality across conversions in either direction.

## Server UI

When running in server mode, you can interact with the tools through the Swagger UI:

1. Open a web browser to http://localhost:8000/docs
2. You'll see a Swagger UI where you can test the tools
3. Click on the tool endpoint, then click "Try it out"
4. Enter the required parameters and execute the request

## Example Output

### Basic Calculator Tool

The basic calculator tool accepts two numbers and an operation and returns a calculation result.

### MCP Logo Tool

The MCP logo tool returns information about MCP and optionally the MCP logo image. 