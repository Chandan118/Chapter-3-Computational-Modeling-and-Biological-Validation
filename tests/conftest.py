"""Pytest configuration and shared fixtures for FormicaBot tests."""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_netlogo():
    """Fixture providing a MockNetLogoLink instance for testing."""
    from netlogo_utils import MockNetLogoLink

    return MockNetLogoLink()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Fixture providing a temporary output directory for test results."""
    output_dir = tmp_path / "experiment_results"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_model_path():
    """Fixture providing a path to a sample NetLogo model."""
    return "final_ants.nlogo"
