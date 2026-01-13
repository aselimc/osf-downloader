"""Shared test configuration and fixtures"""

from pathlib import Path
import pytest
from rich.console import Console

# Test configuration
PROJECT_ID = "ytpuq"
FILE_PATH = "rpp_data.csv"
OUTPUT_DIR = Path("./test_output")


@pytest.fixture
def console():
    """Provide a Rich console for tests"""
    return Console()


@pytest.fixture
def output_dir():
    """Create and provide output directory for test files"""
    OUTPUT_DIR.mkdir(exist_ok=True)
    return OUTPUT_DIR


@pytest.fixture
def project_id():
    """Provide the test project ID"""
    return PROJECT_ID


@pytest.fixture
def file_path():
    """Provide the test file path"""
    return FILE_PATH
