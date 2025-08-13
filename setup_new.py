#!/usr/bin/env python3
"""
Setup configuration for FLL-Sim package.
"""

from setuptools import find_packages, setup

setup(
    name="fll-sim",
    version="1.0.0",
    description="First Lego League Robot and Map Simulator",
    author="FLL-Sim Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pygame>=2.5.0",
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "pymunk>=6.2.0",
        "Pillow>=9.0.0",
        "pyyaml>=6.0",
        "click>=8.0.0",
        "dataclasses-json>=0.5.7",
        "PyQt6>=6.5.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "pre-commit>=2.20.0",
            "coverage"
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ]
)
