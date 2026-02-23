"""
Unit tests for suffix identification functionality

Following TDD - these tests MUST fail initially because CLI doesn't exist yet.

Tests cover:
- Basic suffix identification
- Edge cases (no suffix, ambiguous, OOV words)
- Confidence scoring
- Stem extraction
- POS prediction from suffix
"""
import pytest
import json
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from helpers.cli_runner import CLIRunner


class TestSuffixIdentificationCLI:
    """Test CLI interface for suffix identification"""

    @pytest.fixture
    def cli(self):
        """Create CLI runner instance"""
        return CLIRunner()

    def test_identify_common_noun_suffix(self, cli):
        """Test identifying common noun suffix -ness"""
        # This should fail: CLI doesn't exist yet
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success, f"CLI failed: {result.stderr}"

        data = result.json
        assert data["word"] == "happiness"
        assert data["suffix"] == "-ness"
        assert data["stem"] == "happi"
        assert data["POS"] == "noun"
        assert data["confidence"] > 0.5

    def test_identify_verb_suffix_ing(self, cli):
        """Test identifying verb suffix -ing"""
        result = cli.run(["suffix", "--word", "running"])

        assert result.success
        data = result.json

        assert data["word"] == "running"
        assert data["suffix"] == "-ing"
        assert data["stem"] == "runn"
        # -ing can be verb or noun (gerund)
        assert data["POS"] in ["verb", "noun", ["verb", "noun"]]

    def test_identify_adjective_suffix_able(self, cli):
        """Test identifying adjective suffix -able"""
        result = cli.run(["suffix", "--word", "unbelievable"])

        assert result.success
        data = result.json

        assert data["word"] == "unbelievable"
        assert data["suffix"] == "-able"
        # Should identify stem even with prefix
        assert "believ" in data["stem"] or data["stem"] == "unbeliev"
        assert data["POS"] == "adjective"

    def test_no_suffix_identified(self, cli):
        """Test word with no identifiable suffix"""
        result = cli.run(["suffix", "--word", "cat"])

        assert result.success
        data = result.json

        assert data["word"] == "cat"
        assert data["suffix"] is None
        assert data["stem"] == "cat"
        assert data["confidence"] == 0.0

    def test_minimum_stem_length_respected(self, cli):
        """Test that minimum stem length prevents over-segmentation"""
        # "able" shouldn't be segmented to stem "a" + suffix "ble"
        result = cli.run(["suffix", "--word", "able"])

        assert result.success
        data = result.json

        # Either no suffix identified, or stem length >= 2
        if data["suffix"]:
            assert len(data["stem"]) >= 2
        else:
            assert data["suffix"] is None

    def test_longest_suffix_match_priority(self, cli):
        """Test that longest matching suffix is chosen"""
        # "government" should match "-ment" not "-ent"
        result = cli.run(["suffix", "--word", "government"])

        assert result.success
        data = result.json

        assert data["suffix"] == "-ment"
        assert data["stem"] == "govern"

    def test_confidence_scoring_high_frequency_suffix(self, cli):
        """Test confidence is higher for high-frequency suffixes"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Common suffix -ness should have high confidence
        assert data["confidence"] >= 0.7

    def test_confidence_scoring_low_frequency_suffix(self, cli):
        """Test confidence reflects suffix frequency"""
        # Less common suffix should have lower confidence
        result = cli.run(["suffix", "--word", "foolish"])

        assert result.success
        data = result.json

        assert "confidence" in data
        assert 0.0 <= data["confidence"] <= 1.0

    def test_base_pos_extraction(self, cli):
        """Test extraction of source POS (POS before suffix)"""
        # "happiness" = happy (adjective) + -ness → noun
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        assert "base_POS" in data or "source_POS" in data
        base_pos = data.get("base_POS") or data.get("source_POS")
        assert "adjective" in base_pos or base_pos == "adjective"

    def test_suffix_metadata_included(self, cli):
        """Test that suffix metadata is included in output"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Should include suffix meaning or examples
        assert "suffix_data" in data or "meaning" in data or "examples" in data

    def test_json_output_format(self, cli):
        """Test that output is valid JSON"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success

        # Should not raise json.JSONDecodeError
        data = json.loads(result.stdout)
        assert isinstance(data, dict)

    def test_invalid_word_empty_string(self, cli):
        """Test handling of empty string input"""
        result = cli.run(["suffix", "--word", ""])

        # Should either fail gracefully or return error
        if result.success:
            data = result.json
            assert "error" in data or data["word"] == ""

    def test_invalid_word_numbers(self, cli):
        """Test handling of numeric input"""
        result = cli.run(["suffix", "--word", "12345"])

        assert result.success
        data = result.json

        # Numbers typically have no suffix
        assert data["suffix"] is None

    def test_custom_min_stem_length(self, cli):
        """Test custom minimum stem length parameter"""
        result = cli.run(["suffix", "--word", "happiness", "--min-stem", "3"])

        assert result.success
        data = result.json

        # If suffix identified, stem should be >= 3
        if data["suffix"]:
            assert len(data["stem"]) >= 3

    def test_help_message_displayed(self, cli):
        """Test --help flag shows usage information"""
        result = cli.run(["suffix", "--help"])

        assert result.success or result.exit_code == 0
        # Help should mention 'word' and 'suffix'
        help_text = result.stdout + result.stderr
        assert "word" in help_text.lower()
        assert "suffix" in help_text.lower()


class TestSuffixIdentificationEdgeCases:
    """Test edge cases and corner cases for suffix identification"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_word_ending_in_suffix_but_not_derived(self, cli):
        """Test words that end in suffix pattern but aren't derived forms"""
        # "eness" ends in "-ness" but isn't a real word
        result = cli.run(["suffix", "--word", "oneness"])

        assert result.success
        # Should identify -ness even if word is uncommon
        data = result.json
        assert data["suffix"] == "-ness"

    def test_multiple_suffix_layers(self, cli):
        """Test word with multiple suffixes (only outermost should be identified)"""
        # "nationalization" has -ion and -ation and -ization
        result = cli.run(["suffix", "--word", "nationalization"])

        assert result.success
        data = result.json

        # Should identify outermost suffix
        assert data["suffix"] in ["-ization", "-tion", "-ion"]

    def test_case_insensitivity(self, cli):
        """Test that suffix identification works regardless of case"""
        result1 = cli.run(["suffix", "--word", "happiness"])
        result2 = cli.run(["suffix", "--word", "HAPPINESS"])
        result3 = cli.run(["suffix", "--word", "HaPpInEsS"])

        assert result1.success and result2.success and result3.success

        data1 = result1.json
        data2 = result2.json
        data3 = result3.json

        # All should identify same suffix
        assert data1["suffix"] == data2["suffix"] == data3["suffix"]

    def test_suffix_with_orthographic_changes(self, cli):
        """Test suffixes that cause spelling changes"""
        # "happiness" has stem "happy" but orthography → "happi"
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Stem extraction might show orthographic change
        assert data["stem"] in ["happy", "happi"]

    def test_oov_word_with_valid_suffix(self, cli):
        """Test out-of-vocabulary word with valid suffix pattern"""
        # Made-up word but valid suffix
        result = cli.run(["suffix", "--word", "flurpiness"])

        assert result.success
        data = result.json

        # Should still identify -ness suffix
        assert data["suffix"] == "-ness"
        assert data["stem"] == "flurpi"

    def test_ambiguous_suffix_boundary(self, cli):
        """Test word where suffix boundary is ambiguous"""
        # "singer" could be "sing" + "-er" or "singe" + "-r"
        result = cli.run(["suffix", "--word", "singer"])

        assert result.success
        data = result.json

        # Should choose valid suffix
        assert data["suffix"] in ["-er", "-r"]
        # -er is more likely
        if data["suffix"] == "-er":
            assert data["stem"] == "sing"


class TestSuffixIdentificationIntegration:
    """Integration tests with suffix database"""

    @pytest.fixture
    def cli(self):
        return CLIRunner()

    def test_uses_unified_suffixes_database(self, cli):
        """Test that CLI uses the unified_suffixes.json database"""
        result = cli.run(["suffix", "--word", "happiness"])

        assert result.success
        data = result.json

        # Should have metadata from database
        assert "POS" in data
        # -ness is in the minimal 15-suffix database
        assert data["suffix"] == "-ness"

    def test_missing_database_graceful_failure(self, cli):
        """Test behavior when suffix database is missing"""
        # Use non-existent database path
        result = cli.run([
            "suffix",
            "--word", "happiness",
            "--db", "nonexistent.json"
        ])

        # Should either fail gracefully or return low-confidence result
        if result.success:
            data = result.json
            assert data["confidence"] == 0.0 or "error" in data
        else:
            assert "not found" in result.stderr.lower()

    def test_batch_processing(self, cli):
        """Test processing multiple words in batch"""
        # Test batch mode if implemented
        result = cli.run([
            "suffix",
            "--words", "happiness,running,cats"
        ])

        # May not be implemented yet - that's OK for TDD
        # If implemented, should return multiple results
        if result.success:
            data = result.json
            # Could be list or dict
            assert isinstance(data, (list, dict))
