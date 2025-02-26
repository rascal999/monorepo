from setuptools import setup, find_packages

setup(
    name="mcp-slack-user",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "mcp>=0.1.0",
        "slack-sdk>=3.26.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "markdownify>=0.11.0",
        "uvicorn>=0.24.0",
    ],
)