"""
Apex Algo Trading Engine — package configuration.

Install in development mode:
    pip install -e .

Install as a regular package:
    pip install .
"""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="apex-algo-engine",
    version="0.1.0",
    description="AI-powered automated trading system for futures and forex markets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Apex Algo Trading",
    url="https://github.com/Flowbase23/Apex-Algo",
    packages=find_packages(include=["*"], exclude=["tests", "tests.*"]),
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    # Run the demo with: python demo.py
    # (the demo is a standalone script, not an installed entry point)
)
