"""
Setup configuration for TheBrain MCP Server Python package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="thebrain-mcp",
    version="1.0.0",
    author="",
    description="MCP server for TheBrain API - enables AI assistants to interact with TheBrain knowledge management system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/thebrain-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=[
        "mcp>=1.0.0",
        "python-dotenv>=1.0.0",
        "httpx>=0.25.0",
        "aiofiles>=23.0.0",
        "typing-extensions>=4.9.0",
        "jsonschema>=4.20.0",
    ],
    entry_points={
        "console_scripts": [
            "thebrain-mcp=main:main",
        ],
    },
    include_package_data=True,
)
