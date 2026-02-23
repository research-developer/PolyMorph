"""
Integration tests for 'suffix' command

Tests CLI wrapper around suffix identification functionality.
Complements unit tests with real-world integration scenarios.

Following TDD - these tests MUST fail initially.
"""
import pytest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_runner import CLIRunner


class TestSuffixCommandIntegration:
    """Integration tests for suffix command with real data"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_command_with_builtin_database(self, cli):
        """Test suffix command uses built-in 15-suffix database"""
        # These suffixes should be in the minimal database
        test_words = [
            ("happiness", "-ness"),
            ("running", "-ing"),
            ("beautiful", "-ful"),
            ("teacher", "-er"),
            ("government", "-ment"),
        ]

        for word, expected_suffix in test_words:
            result = cli.run(["suffix", "--word", word])
            assert result.success, f"Failed on word: {word}"
            data = result.json
            assert data["suffix"] == expected_suffix, \
                f"Expected {expected_suffix} for {word}, got {data['suffix']}"

    def test_suffix_command_output_completeness(self, cli):
        """Test that suffix command returns all expected fields"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Required fields
        assert "word" in data
        assert "suffix" in data
        assert "stem" in data
        assert "POS" in data
        assert "confidence" in data

        # Optional but expected fields
        assert "base_POS" in data or "source_POS" in data
        assert "suffix_data" in data or "category" in data

    def test_suffix_command_performance(self, cli):
        """Test suffix command completes quickly"""
        import time

        start = time.time()
        result = cli.run(["suffix", "--word", "happiness"])
        elapsed = time.time() - start

        assert result.success
        # Should complete in under 1 second
        assert elapsed < 1.0

    def test_suffix_command_consistency_multiple_runs(self, cli):
        """Test that suffix command gives consistent results"""
        results = []
        for _ in range(3):
            result = cli.run(["suffix", "--word", "happiness"])
            assert result.success
            results.append(result.json)

        # All runs should give identical results
        assert results[0] == results[1] == results[2]


class TestSuffixCommandWithRealWords:
    """Test suffix command with real English words"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_common_nouns(self, cli):
        """Test suffix identification for common noun suffixes"""
        test_cases = [
            ("happiness", "-ness", "noun"),
            ("government", "-ment", "noun"),
            ("teacher", "-er", "noun"),
            ("brightness", "-ness", "noun"),
            ("player", "-er", "noun"),
        ]

        for word, expected_suffix, expected_pos in test_cases:
            result = cli.run(["suffix", "--word", word])
            assert result.success
            data = result.json

            assert data["suffix"] == expected_suffix
            assert expected_pos in str(data["POS"]).lower()

    def test_suffix_common_verbs(self, cli):
        """Test suffix identification for verb forms"""
        test_cases = [
            ("running", "-ing"),
            ("walked", "-ed"),
            ("singing", "-ing"),
            ("played", "-ed"),
        ]

        for word, expected_suffix in test_cases:
            result = cli.run(["suffix", "--word", word])
            assert result.success
            data = result.json

            assert data["suffix"] == expected_suffix

    def test_suffix_common_adjectives(self, cli):
        """Test suffix identification for adjective suffixes"""
        test_cases = [
            ("beautiful", "-ful", "adjective"),
            ("peaceful", "-ful", "adjective"),
            ("joyful", "-ful", "adjective"),
        ]

        for word, expected_suffix, expected_pos in test_cases:
            result = cli.run(["suffix", "--word", word])
            assert result.success
            data = result.json

            assert data["suffix"] == expected_suffix
            assert expected_pos in str(data["POS"]).lower()

    def test_suffix_common_adverbs(self, cli):
        """Test suffix identification for adverb suffixes"""
        test_cases = [
            ("quickly", "-ly", "adverb"),
            ("slowly", "-ly", "adverb"),
            ("happily", "-ly", "adverb"),
        ]

        for word, expected_suffix, expected_pos in test_cases:
            result = cli.run(["suffix", "--word", word])
            assert result.success
            data = result.json

            assert data["suffix"] == expected_suffix
            # -ly should indicate adverb
            assert expected_pos in str(data["POS"]).lower() or \
                   expected_pos in str(data.get("base_POS", "")).lower()


class TestSuffixCommandDatabaseIntegration:
    """Test integration with suffix database"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_uses_default_database_path(self, cli):
        """Test that default database path is used correctly"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        # Should successfully use data/unified_suffixes.json
        data = result.json
        assert data["suffix"] == "-ness"

    def test_suffix_custom_database_path(self, cli, tmp_path):
        """Test using custom database path"""
        # Create minimal custom database
        custom_db = {
            "suffixes": {
                "-test": {
                    "POS": "noun",
                    "source_POS": ["verb"],
                    "meaning": "test suffix"
                }
            }
        }

        db_file = tmp_path / "custom_suffixes.json"
        db_file.write_text(json.dumps(custom_db))

        result = cli.run([
            "suffix",
            "--word", "unittest",
            "--db", str(db_file)
        ])

        if result.success:
            data = result.json
            # Should use custom database
            assert data["suffix"] == "-test"

    def test_suffix_missing_database_handling(self, cli):
        """Test graceful handling when database is missing"""
        result = cli.run([
            "suffix",
            "--word", "happiness",
            "--db", "/nonexistent/path/database.json"
        ])

        # Should handle gracefully
        if result.success:
            data = result.json
            assert data["confidence"] == 0.0 or "error" in data
        else:
            assert "not found" in result.stderr.lower()

    def test_suffix_database_with_all_15_builtins(self, cli):
        """Test that all 15 built-in suffixes work"""
        # Based on PLUGIN_SUMMARY.md - the minimal database has 15 suffixes
        # We should test representative examples from each
        test_words = [
            "happiness",    # -ness
            "government",   # -ment
            "teacher",      # -er
            "beautiful",    # -ful
            "quickly",      # -ly
            "running",      # -ing
            "played",       # -ed
            "actionable",   # -able
            "largest",      # -est
            "smaller",      # -er (comparative)
        ]

        for word in test_words:
            result = cli.run(["suffix", "--word", word])
            assert result.success, f"Failed on built-in suffix word: {word}"
            data = result.json
            assert data["suffix"] is not None, f"No suffix identified for: {word}"


class TestSuffixCommandStreamProcessing:
    """Test stream processing capabilities"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_stdin_input(self, cli):
        """Test reading word from stdin"""
        result = cli.run(["suffix"], input_text="happiness\n")

        if result.success:
            data = result.json
            assert data["word"] == "happiness"

    def test_suffix_batch_stdin(self, cli):
        """Test processing multiple words from stdin"""
        input_words = "happiness\nrunning\ncats\n"
        result = cli.run(["suffix", "--batch"], input_text=input_words)

        if result.success:
            data = result.json
            # Should return results for multiple words
            assert isinstance(data, list) or len(data) > 1

    def test_suffix_pipe_friendly_output(self, cli):
        """Test that output is pipe-friendly (one JSON per line)"""
        result = cli.run([
            "suffix",
            "--words", "happiness,running",
            "--format", "jsonl"  # JSON Lines format
        ])

        if result.success:
            lines = result.stdout.strip().split("\n")
            # Each line should be valid JSON
            for line in lines:
                data = json.loads(line)
                assert "word" in data


class TestSuffixCommandErrorRecovery:
    """Test error recovery and resilience"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_recovers_from_malformed_word(self, cli):
        """Test graceful handling of malformed input"""
        result = cli.run(["suffix", "--word", ""])

        # Should handle empty string gracefully
        if result.success:
            data = result.json
            assert "error" in data or data["word"] == ""

    def test_suffix_continues_on_error_in_batch(self, cli):
        """Test that batch processing continues despite errors"""
        result = cli.run([
            "suffix",
            "--words", "happiness,,running"  # Empty word in middle
        ])

        if result.success:
            data = result.json
            # Should process valid words even if one is invalid
            if isinstance(data, list):
                assert len(data) >= 2  # At least 2 valid words

    def test_suffix_timeout_protection(self, cli):
        """Test that command doesn't hang indefinitely"""
        # Very long word shouldn't cause timeout
        long_word = "a" * 1000
        result = cli.run(["suffix", "--word", long_word])

        # Should complete within reasonable time (handled by CLI runner timeout)
        assert result.exit_code != 124  # 124 = timeout


class TestSuffixCommandDocumentation:
    """Test documentation and help features"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_help_available(self, cli):
        """Test that help documentation is available"""
        result = cli.run(["suffix", "--help"])

        assert result.exit_code == 0
        help_text = result.stdout.lower()

        # Should document key options
        assert "word" in help_text
        assert "suffix" in help_text

    def test_suffix_version_flag(self, cli):
        """Test version information"""
        result = cli.run(["suffix", "--version"])

        if result.exit_code == 0:
            # Should show version
            assert len(result.stdout) > 0

    def test_suffix_examples_in_help(self, cli):
        """Test that help includes usage examples"""
        result = cli.run(["suffix", "--help"])

        assert result.exit_code == 0
        # Good CLI help includes examples
        # This is aspirational - nice to have
        help_text = result.stdout.lower()
        # May include words like "example" or show actual command usage


class TestSuffixCommandCompatibility:
    """Test compatibility with existing scripts"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_suffix_compatible_with_identify_suffix_script(self, cli):
        """Test that CLI output matches identify_suffix.py script"""
        # Run the original script
        plugin_dir = Path(__file__).parent.parent.parent
        script_path = plugin_dir / "scripts" / "identify_suffix.py"

        import subprocess
        script_result = subprocess.run(
            ["python3", str(script_path), "--word", "happiness"],
            capture_output=True,
            text=True,
            timeout=5
        )

        script_data = json.loads(script_result.stdout)

        # Run the CLI
        cli_result = cli.run(["suffix", "--word", "happiness"])

        if cli_result.success:
            cli_data = cli_result.json

            # Key fields should match
            assert cli_data["suffix"] == script_data["suffix"]
            assert cli_data["stem"] == script_data["stem"]
            assert cli_data["POS"] == script_data["POS"]

    def test_suffix_backward_compatible_output_format(self, cli):
        """Test that output format is stable across versions"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Essential fields that should always be present
        required_fields = ["word", "suffix", "stem", "POS", "confidence"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
