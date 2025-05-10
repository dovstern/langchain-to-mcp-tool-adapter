from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="langchain-to-mcp-tool-adapter",
    version="0.1.1",
    author="LangChain to MCP Tool Adapter Contributors",
    author_email="maintainers@example.com",
    description="Adapter for converting LangChain tools to FastMCP tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dovstern/langchain-to-mcp-tool-adapter",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=[
        "langchain>=0.1.0,<0.4.0",
        "fastmcp>=2.2.0",
        "pydantic>=2.0.0,<3.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=23.0.0",
            "isort>=5.0.0",
            "flake8>=5.0.0",
            "langchain-mcp-adapters",
            "langgraph",
            "langchain-openai",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
    },
) 