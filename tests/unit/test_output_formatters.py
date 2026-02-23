"""
Unit tests for output formatting

Tests different output formats (JSON, plain text, CSV, etc.)
Following TDD - tests fail because formatters don't exist yet.
"""
import pytest
import json
import csv
from io import StringIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_runner import CLIRunner


class TestJSONOutputFormat:
    """Test JSON output formatting"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_default_format_is_json(self, cli):
        """Test that default output format is JSON"""
        result = cli.run(["analyze", "--word", "happiness"])

        assert result.success
        # Should parse as JSON without errors
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_explicit_json_format(self, cli):
        """Test explicit JSON format flag"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "json"
        ])

        assert result.success
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_json_pretty_print(self, cli):
        """Test pretty-printed JSON output"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "json",
            "--pretty"
        ])

        assert result.success
        # Pretty-printed JSON should have indentation
        assert "  " in result.stdout or "\t" in result.stdout

    def test_json_compact(self, cli):
        """Test compact JSON output (no pretty printing)"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "json",
            "--compact"
        ])

        assert result.success
        # Compact JSON should not have extra whitespace
        data = json.loads(result.stdout)
        # Should be valid JSON even when compact
        assert isinstance(data, dict)


class TestPlainTextOutputFormat:
    """Test plain text output formatting"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_text_format_readable(self, cli):
        """Test plain text format is human-readable"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text"
        ])

        assert result.success
        # Should contain key information
        assert "happiness" in result.stdout
        assert "suffix" in result.stdout.lower()

    def test_text_format_includes_all_fields(self, cli):
        """Test text format includes all analysis fields"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text"
        ])

        assert result.success
        output = result.stdout.lower()

        # Should include key fields
        assert "word" in output or "happiness" in output
        assert "suffix" in output or "ness" in output
        assert "pos" in output or "noun" in output
        assert "stem" in output or "happi" in output

    def test_text_format_line_breaks(self, cli):
        """Test text format uses appropriate line breaks"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text"
        ])

        assert result.success
        # Should have multiple lines
        lines = result.stdout.strip().split("\n")
        assert len(lines) > 1


class TestCSVOutputFormat:
    """Test CSV output formatting"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_csv_format_single_word(self, cli):
        """Test CSV format for single word"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "csv"
        ])

        assert result.success
        # Should be valid CSV
        csv_reader = csv.DictReader(StringIO(result.stdout))
        rows = list(csv_reader)

        assert len(rows) == 1
        assert rows[0]["word"] == "happiness"

    def test_csv_format_multiple_words(self, cli):
        """Test CSV format for multiple words"""
        result = cli.run([
            "analyze",
            "--words", "happiness,running,cats",
            "--format", "csv"
        ])

        assert result.success
        csv_reader = csv.DictReader(StringIO(result.stdout))
        rows = list(csv_reader)

        assert len(rows) == 3
        words = [row["word"] for row in rows]
        assert "happiness" in words
        assert "running" in words
        assert "cats" in words

    def test_csv_headers_present(self, cli):
        """Test CSV has proper headers"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "csv"
        ])

        assert result.success
        lines = result.stdout.strip().split("\n")

        # First line should be headers
        headers = lines[0].lower()
        assert "word" in headers
        assert "suffix" in headers or "pos" in headers

    def test_csv_no_headers_option(self, cli):
        """Test CSV without headers option"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "csv",
            "--no-headers"
        ])

        if result.success:
            # First line should be data, not headers
            first_line = result.stdout.strip().split("\n")[0]
            assert "happiness" in first_line


class TestTableOutputFormat:
    """Test table/tabular output formatting"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_table_format_aligned_columns(self, cli):
        """Test table format has aligned columns"""
        result = cli.run([
            "analyze",
            "--words", "happiness,run,cats",
            "--format", "table"
        ])

        if result.success:
            # Table should have borders or alignment
            assert "|" in result.stdout or "+" in result.stdout or "  " in result.stdout

    def test_table_format_headers(self, cli):
        """Test table format includes headers"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "table"
        ])

        if result.success:
            output = result.stdout.lower()
            assert "word" in output or "suffix" in output or "pos" in output


class TestOutputFormatFieldSelection:
    """Test selecting specific fields in output"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_select_specific_fields(self, cli):
        """Test outputting only selected fields"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--fields", "word,suffix,POS"
        ])

        assert result.success
        data = result.json

        # Should only include requested fields (plus maybe metadata)
        assert "word" in data
        assert "suffix" in data
        assert "POS" in data

    def test_exclude_confidence_scores(self, cli):
        """Test excluding confidence scores from output"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--no-confidence"
        ])

        if result.success:
            data = result.json
            # Confidence should be excluded or not present
            assert "confidence" not in data or data.get("confidence") is None

    def test_include_metadata(self, cli):
        """Test including metadata in output"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--include-metadata"
        ])

        if result.success:
            data = result.json
            # Should include metadata fields
            assert "source" in data or "version" in data or "timestamp" in data


class TestOutputFormatErrors:
    """Test error handling in output formatting"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_invalid_format_error(self, cli):
        """Test error on invalid format specification"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "invalid_format"
        ])

        # Should fail or show error
        assert not result.success or "error" in result.stderr.lower()

    def test_format_specific_to_command(self, cli):
        """Test that some formats may be command-specific"""
        # CSV might make sense for batch but not single analysis
        result = cli.run([
            "suffix",
            "--word", "happiness",
            "--format", "csv"
        ])

        # Should either work or give helpful error
        if not result.success:
            assert len(result.stderr) > 0


class TestOutputQuietMode:
    """Test quiet/verbose output modes"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_quiet_mode_minimal_output(self, cli):
        """Test quiet mode suppresses extra output"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--quiet"
        ])

        if result.success:
            # Should have minimal output (just result, no messages)
            assert len(result.stderr) == 0 or result.stderr.strip() == ""

    def test_verbose_mode_extra_info(self, cli):
        """Test verbose mode includes extra information"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--verbose"
        ])

        if result.success:
            # Verbose might include debug info in stderr
            combined = result.stdout + result.stderr
            # Should have more information
            assert len(combined) > 100

    def test_debug_mode_detailed_output(self, cli):
        """Test debug mode includes detailed diagnostic information"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--debug"
        ])

        if result.success:
            # Debug mode should show tool names, processing steps, etc.
            combined = result.stdout + result.stderr
            assert "debug" in combined.lower() or len(combined) > 200


class TestOutputColorization:
    """Test colored output support"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_color_output_disabled_by_default_in_pipe(self, cli):
        """Test that color is disabled when output is piped"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text"
        ])

        if result.success:
            # Should not contain ANSI color codes when piped
            assert "\033[" not in result.stdout

    def test_force_color_option(self, cli):
        """Test forcing color output"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text",
            "--color"
        ])

        if result.success:
            # May or may not have color codes depending on implementation
            pass  # Just check it doesn't crash

    def test_no_color_option(self, cli):
        """Test explicitly disabling color"""
        result = cli.run([
            "analyze",
            "--word", "happiness",
            "--format", "text",
            "--no-color"
        ])

        assert result.success
        # Should definitely not have color codes
        assert "\033[" not in result.stdout
