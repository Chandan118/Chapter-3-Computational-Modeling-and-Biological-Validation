"""Smoke tests for experiment runners."""

import pytest


class TestExperimentOutputs:
    """Test suite for experiment output handling."""

    def test_results_directory_creation(self, temp_output_dir):
        """Test that results directory structure is created correctly."""
        assert temp_output_dir.exists()
        assert temp_output_dir.is_dir()

    def test_json_output_creation(self, temp_output_dir):
        """Test that JSON output files can be created."""
        output_file = temp_output_dir / "test_colony1_trial1.json"

        import json

        data = {
            "colony": 1,
            "trial": 1,
            "ticks": [0, 10, 20],
            "ants_foraging": [50, 52, 48],
            "chemical": [0.5, 0.55, 0.52],
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)

        assert output_file.exists()

        # Verify we can read it back
        with open(output_file, "r") as f:
            loaded = json.load(f)

        assert loaded["colony"] == 1
        assert len(loaded["ticks"]) == 3
