from setuptools import setup, find_packages

setup(
    name="trAIder",
    version="0.1.0",
    packages=find_packages(include=['app', 'app.*']),
    install_requires=[
        "pytest==7.4.3",
        "requests==2.31.0",
        "jinja2==3.1.2",
        "openai==1.3.7",
        "beautifulsoup4==4.12.2",
        "python-dotenv==1.0.0",
        "pytest-mock==3.12.0",
        "pytest-cov==4.1.0"
    ],
    python_requires=">=3.10",
)