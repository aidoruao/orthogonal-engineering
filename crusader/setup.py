"""
Crusader Combat Refrigerator - Package Setup
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Setup configuration for the Crusader Combat Refrigerator package.
Enables installation via pip and proper package resolution.
"""

import os

from setuptools import find_packages, setup

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
requirements = []
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [
            line.strip() for line in fh if line.strip() and not line.startswith("#")
        ]
except FileNotFoundError:
    # Fallback to minimal requirements
    requirements = [
        "psutil>=5.9.0",
        "watchdog>=3.0.0",
        "aiofiles>=23.1.0",
        "aiosqlite>=0.19.0",
        "PyYAML>=6.0",
        "toml>=0.10.2",
        "json5>=0.9.14",
        "ujson>=5.8.0",
        "cryptography>=41.0.0",
        "pycryptodome>=3.19.0",
        "ecdsa>=0.18.0",
        "Flask>=3.0.0",
        "Flask-CORS>=4.0.0",
        "requests>=2.31.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "scipy>=1.11.0",
        "Pillow>=10.0.0",
        "gpiozero>=1.6.2",
        "structlog>=23.1.0",
        "loguru>=0.7.0",
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "pytest-mock>=3.11.0",
        "hypothesis>=6.85.0",
        "black>=23.9.0",
        "flake8>=6.1.0",
        "mypy>=1.5.0",
        "isort>=5.12.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.5.0",
        "ipython>=8.15.0",
        "debugpy>=1.8.0",
        "pydantic>=2.4.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "Werkzeug>=2.3.0,<3.0.0",
        "Jinja2>=3.1.0,<4.0.0",
        "MarkupSafe>=2.1.0,<3.0.0",
        "cffi>=1.15.0",
        "pycparser>=2.21",
        "setuptools>=65.0.0",
        "packaging>=23.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "tzlocal>=5.0.1",
    ]

# Package version
version = "1.0.0"

setup(
    name="crusader-refrigerator",
    version=version,
    author="Orthogonal Engineering Framework",
    author_email="noreply@orthogonal.engineering",
    description="Advanced fly warfare system for refrigerators using orthogonal engineering principles",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aidoruao/orthogonal-engineering/crusader",
    packages=find_packages(include=["crusader", "crusader.*"]),
    package_dir={"": "."},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering",
        "Topic :: Home Automation",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Natural Language :: English",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "twine>=4.0.0",
            "build>=0.10.0",
        ],
        "simulation": [
            "pygame>=2.0.0",  # For hardware simulation visualization
            "matplotlib>=3.0.0",  # For data visualization
        ],
        "hardware": [
            "RPi.GPIO>=0.7.0",  # Raspberry Pi GPIO access
            "smbus2>=0.4.0",  # I2C communication
            "spidev>=3.0.0",  # SPI communication
            "Adafruit-Blinka>=8.0.0",  # CircuitPython support
            "adafruit-circuitpython-busdevice>=5.0.0",
            "adafruit-circuitpython-dht>=3.7.0",
            "adafruit-circuitpython-ds18x20>=1.4.7",  # Downgraded version
            "adafruit-circuitpython-bmp280>=3.5.0",
        ],
        "full": [
            "opencv-python>=4.8.0",
            "imageio>=2.31.0",
            "scikit-learn>=1.3.0",
            "Flask-SocketIO>=5.3.0",
            "websockets>=12.0",
            "sentry-sdk>=1.35.0",
            "redis>=5.0.0",
            "prometheus-client>=0.18.0",
            "boto3>=1.28.0",
            "google-cloud-storage>=2.10.0",
            "azure-storage-blob>=12.18.0",
            "numba>=0.58.0",
            "cython>=3.0.0",
            "jupyter>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crusader=crusader.core.main:main",
            "crusader-simulate=crusader.core.main:simulate_main",
            "crusader-diagnose=crusader.monitoring.diagnostics:diagnose_main",
            "crusader-test=crusader.tests.test_warfare:test_main",
        ],
    },
    package_data={
        "crusader": [
            "core/config.yaml",
            "hardware/pins.yaml",
            "docs/*.md",
            "scripts/*.sh",
        ],
    },
    data_files=[
        ("share/crusader", ["LICENSE.md", "README.md", "crusader.service"]),
        ("etc/crusader", ["core/config.yaml"]),
        ("lib/systemd/system", ["crusader.service"]),
    ],
    include_package_data=True,
    project_urls={
        "Bug Reports": "https://github.com/aidoruao/orthogonal-engineering/issues",
        "Source": "https://github.com/aidoruao/orthogonal-engineering/crusader",
        "Documentation": "https://github.com/aidoruao/orthogonal-engineering/crusader/docs",
    },
    license="AGAPE (Free Forever)",
    keywords=[
        "refrigerator",
        "pest-control",
        "iot",
        "raspberry-pi",
        "automation",
        "orthogonal-engineering",
        "warfare-system",
        "fly-control",
        "biocontrol",
        "uv-sterilization",
    ],
)
