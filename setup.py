from setuptools import setup, find_packages

setup(
    name="md-to-yaml",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
        "pyyaml>=6.0.1",
        "pytest>=7.0.0",
        "pytest-asyncio>=0.23.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0"
    ],
) 